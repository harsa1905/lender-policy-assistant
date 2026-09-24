import json
import math
import os
import sys
import threading
import time
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_index.core import Settings

from src import query as query_module
from src import answer_library
from src.query import query_policies
from src.config import (
    QUERY_CACHE_PATH, QUERY_CACHE_PREFILTER_THRESHOLD, QUERY_CACHE_MAX_CANDIDATES,
    QUERY_CACHE_ENABLED, ANSWER_LIBRARY_ENABLED, CHUNKS_DIR, PROJECT_ROOT,
)
from src.ingest import parse_chunk_file, ingest_chunks, split_chunk_blocks, VALID_LENDERS
from scripts.draft_chunks import draft_chunks_from_pdfs, VISION_MODEL

app = FastAPI(title="LifeX Policy Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_query_cache_lock = threading.Lock()
_promote_lock = threading.Lock()

LENDERS = ["BFS", "Resimac", "Westpac", "CFAL", "Angle", "Flexi", "Metro"]


class _IndexRWLock:
    """Guards access to the module-level Chroma collection/index in
    src.query. Plain mutual exclusion (reusing one threading.Lock for both
    /query and /chunks/promote) would fix the race below at the cost of a
    worse, far more common regression: every concurrent query would
    serialize behind every other query, not just behind a promotion, since
    FastAPI's sync routes each acquire the same lock for their full
    duration. A promotion is a rare, admin-triggered ~30-40s event, so this
    only needs writers (promote) to be exclusive against readers (query) --
    concurrent readers must still run in parallel with each other, which is
    the actual common case for multiple brokers querying at once.

    ingest_chunks() deletes and recreates the "lifex_policies" Chroma
    collection through its own client, then reload_index() re-points
    query.py's module-level globals at the fresh one -- a query that reads
    those globals mid-rebuild can hit a deleted collection or a
    half-initialised index. acquire_write() blocks until every in-flight
    reader has released, and blocks new readers from starting once a writer
    is waiting, so /chunks/promote never overlaps a live /query call.
    """
    def __init__(self):
        self._readers = 0
        self._cond = threading.Condition(threading.Lock())

    def acquire_read(self):
        with self._cond:
            self._readers += 1

    def release_read(self):
        with self._cond:
            self._readers -= 1
            if self._readers == 0:
                self._cond.notify_all()

    def acquire_write(self):
        self._cond.acquire()
        while self._readers > 0:
            self._cond.wait()

    def release_write(self):
        self._cond.release()


_index_lock = _IndexRWLock()

# Drafts are never written straight into data/chunks/ -- they land here
# first and only move to the live file below via an explicit /chunks/promote
# call, mirroring this project's established "no auto-promotion, a human
# reviews the diff first" rule (see scripts/draft_chunks.py's own docstring).
CHUNKS_DRAFT_DIR = str(PROJECT_ROOT / "data" / "chunks_draft")
# Uploaded source PDFs are kept here too, purely as a provenance/audit
# trail ("why does this chunk say X" -> here's the exact file that was
# uploaded) -- separate from data/documents/, which is the already-ingested,
# already-reviewed live set.
UPLOADS_DIR = str(PROJECT_ROOT / "data" / "documents_pending")

# Which physical file in data/chunks/ each lender's live chunks live in.
# Not derivable automatically -- filenames carry historical "_v2" suffixes
# from earlier corrections, so this mapping is the source of truth
# /chunks/promote uses to know which file to merge a draft into.
LENDER_CHUNK_FILE = {
    "ANGLE": "angle_chunks.md",
    "BFS": "bfs_chunks_v2.md",
    "CFAL": "cfal_chunks_v2.md",
    "FLEXI": "flexi_chunks.md",
    "METRO": "metro_chunks.md",
    "RESIMAC": "resimac_chunks_v2.md",
    "WESTPAC": "westpac_chunks_v2.md",
}

def _split_raw_chunks(text: str):
    """Split a chunk .md file's raw text into (header, {chunk_id: block},
    [chunk_id order]) without going through parse_chunk_file -- that
    function returns Document objects built for embedding, discarding the
    original markdown block text. Promotion needs the exact original block
    text so unrelated chunks in the same file are preserved byte-for-byte
    when only a few chunk_ids are being upserted.

    Thin wrapper over src.ingest.split_chunk_blocks -- the actual splitting
    rules live there now, shared with parse_chunk_file() and
    get_all_chunk_blocks() (three separate copies of this same regex used to
    exist, risking silent drift if the chunk-file format ever changed)."""
    return split_chunk_blocks(text)


def _render_chunk_file(header: str, blocks: dict, order: list) -> str:
    sections = [header.rstrip("\n")] if header.strip() else []
    sections.extend(blocks[cid] for cid in order)
    return "\n---\n".join(sections) + "\n"


def _embed(text: str):
    # Same embedding model used for retrieval — comparing question meaning,
    # not just word overlap, so e.g. "primary assets" vs "secondary assets"
    # (same words otherwise, different correct answer) doesn't false-match.
    return Settings.embed_model.get_query_embedding(text)


def _cosine_similarity(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _load_query_cache():
    if os.path.exists(QUERY_CACHE_PATH):
        with open(QUERY_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _find_cached(question: str):
    """Two-stage cache lookup -- see QUERY_CACHE_PREFILTER_THRESHOLD's
    comment in config.py for why embedding similarity alone isn't a safe
    gate for this domain. Stage 1 (cheap): embedding similarity narrows the
    whole cache down to a handful of plausible candidates, ordered best
    first. Stage 2 (a small LLM call per candidate, capped at
    QUERY_CACHE_MAX_CANDIDATES): the actual yes/no gate, checked in
    similarity order so the most plausible match is tried first -- returns
    on the first candidate that passes, or None if none do."""
    q_embedding = _embed(question)
    scored = []
    for entry in _load_query_cache():
        score = _cosine_similarity(q_embedding, entry["embedding"])
        if score >= QUERY_CACHE_PREFILTER_THRESHOLD:
            scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)

    for _, entry in scored[:QUERY_CACHE_MAX_CANDIDATES]:
        if query_module.questions_require_same_answer(question, entry["question"]):
            return entry
    return None


def _invalidate_query_cache_for_chunks(changed_chunk_ids: set) -> int:
    """Drop every cached answer that cited one of these chunk_ids, and return
    how many were removed.

    Chunk edits used to leave the query cache completely untouched, so after
    a rate change the cache kept serving the OLD figure indefinitely: ask a
    question, update the chunk, ask again -- cache hit, superseded number,
    no signal that anything was stale. Nothing expired it either; entries
    carry no timestamp, so age isn't even knowable.

    Dropping is the right move here, and deliberately different from what
    the answer library does with the same event. Library entries are human
    corrections worth preserving, so those get individually re-checked and
    rewritten or flagged. A query-cache entry is just an unreviewed LLM
    answer with nothing worth salvaging -- regenerating it costs one
    question's latency and is guaranteed to reflect the new chunk.

    Precise rather than blunt because entries record the sources they drew
    on, so "did this answer depend on what changed?" is answerable directly.
    """
    if not changed_chunk_ids:
        return 0
    with _query_cache_lock:
        cache = _load_query_cache()
        survivors = [
            entry for entry in cache
            if not any(s.get("chunk_id") in changed_chunk_ids for s in (entry.get("sources") or []))
        ]
        removed = len(cache) - len(survivors)
        if removed:
            _write_query_cache(survivors)
        return removed


def _clear_query_cache() -> int:
    """Empty the cache wholesale, returning how many entries were dropped.

    For the path where chunks were edited by hand and re-ingested outside
    /chunks/promote: nothing recorded which chunk_ids moved, and cache
    entries don't snapshot chunk content the way library entries do, so
    there's no way to tell which are stale. Clearing everything is the only
    honest option, and a cheap one -- the cache is fully regenerable and the
    cost is one slow answer per question afterwards.
    """
    with _query_cache_lock:
        cache = _load_query_cache()
        if cache:
            _write_query_cache([])
        return len(cache)


def _write_query_cache(cache: list):
    """Atomic write, shared by every cache mutation (append, invalidate, clear).

    Writes a temp file then replaces, rather than truncating the real file in
    place. FastAPI's sync endpoints run in a thread pool, so a concurrent
    request's unlocked _load_query_cache read could otherwise land mid-write
    and hit half-written, invalid JSON. os.replace is atomic on both Windows
    and POSIX, so a concurrent reader always sees either the old file or the
    new one, whole.
    """
    os.makedirs(os.path.dirname(QUERY_CACHE_PATH), exist_ok=True)
    tmp_path = QUERY_CACHE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)
    os.replace(tmp_path, QUERY_CACHE_PATH)


def _append_to_query_cache(question: str, answer: str, sources: list):
    with _query_cache_lock:
        cache = _load_query_cache()
        q_embedding = _embed(question)

        # Purge any existing entry the gate considers the same question
        # before adding this fresh one. Without this, asking the same (or a
        # paraphrased) question across separate runs just keeps appending --
        # nothing ever dedupes or expires -- so duplicate entries pile up
        # with no recency signal between them. _find_cached ranks purely by
        # embedding similarity, so with several near-identical entries it's
        # essentially arbitrary which one answers a later request. Confirmed
        # in practice: three duplicate entries for the same question, one of
        # them a stale wrong answer from an earlier run, sitting alongside
        # two correct ones with no way to prefer the current generation.
        # Keeping this to one entry per distinct question removes that
        # failure mode outright rather than just making it less likely.
        survivors = []
        for entry in cache:
            score = _cosine_similarity(q_embedding, entry["embedding"])
            if score >= QUERY_CACHE_PREFILTER_THRESHOLD and query_module.questions_require_same_answer(question, entry["question"]):
                continue  # superseded by the fresh answer being cached now
            survivors.append(entry)
        cache = survivors

        cache.append({
            "question": question,
            "answer": answer,
            "sources": sources,
            "embedding": q_embedding,
        })
        _write_query_cache(cache)


class HistoryTurn(BaseModel):
    question: str
    answer: str


class QueryRequest(BaseModel):
    question: str
    history: list[HistoryTurn] = []


class Source(BaseModel):
    chunk_id: str
    lender: str
    intent: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    response_time: float
    from_cache: bool
    # "generated" (fresh LLM answer), "cache" (unreviewed semantic cache
    # hit), or "library" (a human-reviewed/corrected answer_library entry).
    # Additive field -- existing frontend code only reads from_cache/answer
    # and can ignore this safely.
    answer_source: str = "generated"


class HealthResponse(BaseModel):
    status: str
    lenders: list[str]
    chunks: int


class SaveAnswerRequest(BaseModel):
    question: str
    answer: str
    chunk_ids: list[str]


class SaveAnswerResponse(BaseModel):
    status: str
    entry_id: int


class DraftChunkItem(BaseModel):
    chunk_id: str
    is_new: bool  # False = this chunk_id already exists in the live file (this is an update, not an addition)
    draft_content: str
    existing_content: str | None = None


class DraftResponse(BaseModel):
    draft_id: str
    lender: str
    source_filename: str
    chunks: list[DraftChunkItem]
    warnings: list[str]


class PromoteRequest(BaseModel):
    draft_id: str
    lender: str
    # Which chunk_ids from the draft to promote. Omit/null to promote every
    # chunk the draft produced -- letting the reviewer promote only some of
    # them is what makes "the model drafted 5 chunks but 1 looks wrong" a
    # non-blocking problem instead of an all-or-nothing choice.
    chunk_ids: list[str] | None = None


class AnswerLibraryUpdate(BaseModel):
    id: int
    question: str
    status: str
    note: str


class PromoteResponse(BaseModel):
    status: str
    lender: str
    promoted_chunk_ids: list[str]
    total_chunks_in_file: int
    total_chunks_in_index: int
    # Saved answer_library entries that depended on the promoted chunk_ids
    # and were auto-updated or flagged needs_review as a result -- surfaces
    # the ripple effect of this promotion instead of it happening silently.
    answer_library_updates: list[AnswerLibraryUpdate]
    # How many unreviewed cached answers cited a promoted chunk and were
    # dropped. The other half of that ripple: without it, stale cached
    # answers would keep being served with nothing to indicate they predate
    # the change. Additive field -- existing frontend code can ignore it.
    query_cache_invalidated: int = 0


def _sources_for_chunk_ids(chunk_ids: list) -> list:
    """Look up lender/intent metadata for a saved answer_library entry's
    chunk_ids -- unlike a fresh retrieval, a library/cache hit has no
    similarity score, so 1.0 stands in for "this is simply the answer",
    not a ranked match.

    Chroma's own primary ids are auto-generated per-node UUIDs (the
    SentenceSplitter transformation in ingest_chunks() splits each Document
    into node(s), each with its own id -- chunk_id only survives as a
    metadata field, not the primary id), so this has to filter on the
    chunk_id metadata field via `where`, not collection.get(ids=...). A
    chunk near the CHUNK_SIZE safety-net threshold can be split into more
    than one node sharing the same chunk_id, so this also has to dedupe by
    chunk_id -- otherwise a single chunk can show up twice in the response's
    sources list."""
    if not chunk_ids:
        return []
    result = query_module._chroma_collection.get(
        where={"chunk_id": {"$in": chunk_ids}}, include=["metadatas"]
    )
    seen = {}
    for meta in result["metadatas"]:
        cid = meta.get("chunk_id", "unknown")
        if cid in seen:
            continue
        seen[cid] = Source(
            chunk_id=cid,
            lender=meta.get("lenders", "unknown"),
            intent=meta.get("topic_intent", "unknown"),
            score=1.0,
        )
    return list(seen.values())


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    # Read-locked for the whole handler (simplest correct boundary, given
    # the index/collection is touched from several call paths below spread
    # across this module and query.py) -- see _IndexRWLock's docstring for
    # why this is a reader lock, not the same lock /chunks/promote uses.
    _index_lock.acquire_read()
    try:
        return _query_impl(request)
    finally:
        _index_lock.release_read()


def _query_impl(request: QueryRequest):
    start = time.time()

    history = [h.model_dump() for h in request.history]

    # A broker correcting the assistant's last answer directly in chat
    # ("no, that rate is actually 7.15%") is not a new question, so it must
    # be checked before anything else -- otherwise it would either get
    # matched against the library/cache as if it were a real query, or fall
    # through to the main pipeline and get answered as one. Per-project
    # decision: chat corrections are saved and served back immediately, no
    # separate approval step (unlike the Review tab's AI-generated answers).
    if history:
        correction = query_module.detect_and_apply_correction(request.question, history)
        if correction:
            entry = answer_library.save_entry(
                correction["original_question"],
                correction["corrected_answer"],
                correction["chunk_ids"],
            )
            return QueryResponse(
                answer="Got it — I've corrected that and saved it, so future questions like this will get the updated answer.",
                sources=_sources_for_chunk_ids(entry.get("chunk_ids", [])),
                response_time=time.time() - start,
                from_cache=False,
                answer_source="correction_saved",
            )

    # Both checks below are skipped for follow-ups -- a follow-up only
    # makes sense in the context of its own conversation, so matching it
    # against an unrelated standalone question's cached/corrected answer
    # would return something that doesn't actually address it.
    if not request.history:
        if ANSWER_LIBRARY_ENABLED:
            entry = answer_library.find_best_match(request.question)
            if entry:
                return QueryResponse(
                    answer=entry["answer"],
                    sources=_sources_for_chunk_ids(entry.get("chunk_ids", [])),
                    response_time=time.time() - start,
                    from_cache=True,
                    answer_source="library",
                )

        if QUERY_CACHE_ENABLED:
            cached = _find_cached(request.question)
            if cached:
                return QueryResponse(
                    answer=cached["answer"],
                    sources=[Source(**s) for s in cached["sources"]],
                    response_time=time.time() - start,
                    from_cache=True,
                    answer_source="cache",
                )

    try:
        answer, nodes = query_policies(request.question, verbose=False, history=history)
    except Exception as e:
        # Without this, an unhandled exception here (OpenAI down after all
        # retries, a ChromaDB hiccup, etc.) surfaces to the frontend as a
        # generic connection failure indistinguishable from "the backend
        # isn't running at all" — the exact confusing failure mode already
        # diagnosed once before in this project for an unrelated bug. A
        # distinct 503 at least tells the frontend/broker the backend is up
        # but the question itself failed, so they know to just retry.
        raise HTTPException(status_code=503, detail=f"Couldn't process that question — please try again. ({type(e).__name__})")
    elapsed = time.time() - start

    sources = [
        Source(
            chunk_id=node.metadata.get("chunk_id", "unknown"),
            lender=node.metadata.get("lenders", "unknown"),
            intent=node.metadata.get("topic_intent", "unknown"),
            score=node.score,
        )
        for node in nodes
    ]

    if QUERY_CACHE_ENABLED and not request.history:
        _append_to_query_cache(request.question, answer, [s.model_dump() for s in sources])

    return QueryResponse(
        answer=answer,
        sources=sources,
        response_time=elapsed,
        from_cache=False,
    )


@app.get("/health", response_model=HealthResponse)
def health():
    from src.query import _chroma_collection

    return HealthResponse(status="ok", lenders=LENDERS, chunks=_chroma_collection.count())


@app.post("/answer-library/save", response_model=SaveAnswerResponse)
def save_answer(request: SaveAnswerRequest):
    """Request/response shape is unchanged from before -- the existing
    frontend Review tab already calls this exact endpoint when a reviewer
    approves (optionally hand-edited) an answer. What changed is internal:
    saved entries now also get a question embedding and a snapshot of every
    chunk_id's current content, so they can be served back at query time
    (see /query's answer_library.find_best_match check) and checked for
    staleness later (see /answer-library/refresh and /chunks/promote)."""
    entry = answer_library.save_entry(request.question, request.answer, request.chunk_ids)
    return SaveAnswerResponse(status="saved", entry_id=entry["id"])


class RefreshEntryResult(BaseModel):
    id: int
    question: str
    status: str
    note: str


class RefreshResponse(BaseModel):
    checked: int
    updated: list[RefreshEntryResult]


@app.post("/answer-library/refresh", response_model=RefreshResponse)
def refresh_answer_library():
    """Re-check every saved answer against the CURRENT content of the
    chunks it depends on, and auto-update or flag anything that's drifted.

    /chunks/promote already triggers this automatically, scoped to just the
    chunks it changed. This endpoint exists for the other path: chunks
    edited by hand and re-ingested outside the promote flow (e.g. via
    `python -m src.ingest`), where nothing recorded which chunk_ids moved --
    call this once afterwards to catch anything that needs it.

    Also empties the query cache. On this path nothing recorded which chunks
    moved, and cache entries don't snapshot chunk content the way library
    entries do, so there's no way to tell which cached answers are now stale
    -- clearing all of them is the only honest option. Cheap, since the cache
    is fully regenerable; the cost is one slow answer per question after."""
    entries = answer_library.load_entries()
    touched = answer_library.refresh_stale_entries()
    _clear_query_cache()
    return RefreshResponse(
        checked=len(entries),
        updated=[
            RefreshEntryResult(id=e["id"], question=e["question"], status=e["status"], note=e.get("note", ""))
            for e in touched
        ],
    )


class CacheStatsResponse(BaseModel):
    cached_answers: int
    library_answers: int


@app.get("/query-cache/stats", response_model=CacheStatsResponse)
def query_cache_stats():
    """Current size of both answer stores, for the UI to show before offering
    to clear one of them."""
    return CacheStatsResponse(
        cached_answers=len(_load_query_cache()),
        library_answers=len(answer_library.load_entries()),
    )


class ClearCacheResponse(BaseModel):
    status: str
    cleared: int


@app.post("/query-cache/clear", response_model=ClearCacheResponse)
def clear_query_cache():
    """Empty the query cache (unreviewed AI answers only).

    Deliberately scoped to the cache and NOT the answer library: the cache is
    fully regenerable, so clearing it costs one slow answer per question,
    whereas the library holds human corrections that nothing else can
    reconstruct. Losing those to a mis-click during a demo is not a
    recoverable mistake, so this endpoint simply cannot do it.

    Useful when chunks or prompts have changed and you want every answer
    regenerated rather than served from before the change -- chunk
    promotions invalidate affected entries automatically (see
    _invalidate_query_cache_for_chunks), but a code or prompt change leaves
    the cache technically valid and semantically stale.
    """
    cleared = _clear_query_cache()
    return ClearCacheResponse(status="cleared", cleared=cleared)


@app.post("/chunks/draft", response_model=DraftResponse)
def draft_chunks(lender: str = Form(...), file: UploadFile = File(...)):
    """Upload a single lender policy PDF and have it auto-drafted into
    chunk markdown. Never touches data/chunks/ -- the draft is written only
    to data/chunks_draft/, keyed by the returned draft_id, and does nothing
    to the live index until /chunks/promote is called with that id."""
    lender_code = lender.strip().upper()
    if lender_code not in VALID_LENDERS:
        raise HTTPException(status_code=400, detail=f"Unknown lender '{lender}'. Must be one of {sorted(VALID_LENDERS)}")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    pdf_bytes = file.file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Kept purely as an audit trail (which exact file produced which draft)
    # -- separate from data/documents/, the already-reviewed live set.
    upload_dir = os.path.join(UPLOADS_DIR, lender_code)
    os.makedirs(upload_dir, exist_ok=True)
    stored_name = f"{int(time.time())}_{file.filename}"
    with open(os.path.join(upload_dir, stored_name), "wb") as f:
        f.write(pdf_bytes)

    try:
        draft_text = draft_chunks_from_pdfs(lender_code, [(file.filename, pdf_bytes)], model=VISION_MODEL)
    except Exception as e:
        # A vision-model/API failure here should read as "try again", not
        # as a broken server -- same reasoning as the /query 503 above.
        raise HTTPException(status_code=502, detail=f"Auto-chunking failed: {type(e).__name__}: {e}")

    if not draft_text.strip():
        raise HTTPException(status_code=502, detail="Auto-chunking produced no output")

    draft_id = f"{lender_code.lower()}_{uuid.uuid4().hex[:8]}"
    os.makedirs(CHUNKS_DRAFT_DIR, exist_ok=True)
    draft_path = os.path.join(CHUNKS_DRAFT_DIR, f"{draft_id}.md")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(draft_text)

    warnings = []
    parse_chunk_file(draft_path, warnings)  # schema validation only -- discard the Document objects

    _, draft_blocks, draft_order = _split_raw_chunks(draft_text)
    if not draft_order:
        raise HTTPException(status_code=502, detail="Auto-chunking produced no recognisable '## chunk_id:' sections")

    live_filename = LENDER_CHUNK_FILE.get(lender_code)
    existing_blocks = {}
    if live_filename:
        live_path = os.path.join(CHUNKS_DIR, live_filename)
        if os.path.exists(live_path):
            with open(live_path, "r", encoding="utf-8") as f:
                _, existing_blocks, _ = _split_raw_chunks(f.read())

    chunks = [
        DraftChunkItem(
            chunk_id=cid,
            is_new=cid not in existing_blocks,
            draft_content=draft_blocks[cid],
            existing_content=existing_blocks.get(cid),
        )
        for cid in draft_order
    ]

    return DraftResponse(
        draft_id=draft_id,
        lender=lender_code,
        source_filename=file.filename,
        chunks=chunks,
        warnings=warnings,
    )


@app.post("/chunks/promote", response_model=PromoteResponse)
def promote_chunks(request: PromoteRequest):
    """Merge selected chunk_ids from a previously-drafted file into the
    lender's live chunk file (upsert by chunk_id -- untouched chunks in that
    file are preserved byte-for-byte), then re-ingest so the change is live
    immediately. This is the only path that ever writes to data/chunks/ as
    part of this pipeline -- there is no automatic promotion anywhere."""
    lender_code = request.lender.strip().upper()
    live_filename = LENDER_CHUNK_FILE.get(lender_code)
    if not live_filename:
        raise HTTPException(status_code=400, detail=f"No live chunk file mapped for lender '{lender_code}'")

    draft_path = os.path.join(CHUNKS_DRAFT_DIR, f"{request.draft_id}.md")
    if not os.path.exists(draft_path):
        raise HTTPException(status_code=404, detail=f"Draft '{request.draft_id}' not found — check the draft id, or re-upload the PDF to create a new draft")

    # draft_id and lender arrive as independent fields, so nothing stopped a
    # caller pairing one lender's draft with another lender's name -- which
    # would merge, say, Angle's chunks straight into westpac_chunks_v2.md.
    # /chunks/draft builds the id as "<lender>_<uuid>", so the draft already
    # carries which lender it was made for; trust that over the request. No
    # lender code contains an underscore, so the prefix split is unambiguous.
    # The frontend always sends a matching pair, so this guards direct API
    # use and any future UI bug rather than a live failure.
    draft_lender = request.draft_id.split("_")[0].upper()
    if draft_lender != lender_code:
        raise HTTPException(
            status_code=400,
            detail=(f"Draft '{request.draft_id}' was drafted for {draft_lender}, but this request asks to "
                    f"promote it into {lender_code}'s chunk file. Promote it as {draft_lender}, or re-draft "
                    f"the PDF under {lender_code}."),
        )

    with open(draft_path, "r", encoding="utf-8") as f:
        draft_text = f.read()
    _, draft_blocks, draft_order = _split_raw_chunks(draft_text)

    selected_ids = request.chunk_ids if request.chunk_ids is not None else draft_order
    unknown = [cid for cid in selected_ids if cid not in draft_blocks]
    if unknown:
        raise HTTPException(status_code=400, detail=f"chunk_id(s) not found in this draft: {unknown}")
    if not selected_ids:
        raise HTTPException(status_code=400, detail="No chunk_ids selected to promote")

    with _promote_lock:
        # Serializes concurrent promotions against each other (two promotes
        # racing on the same live_path would otherwise read-modify-write it
        # unsafely). This does NOT touch the chroma index, so queries can
        # still run concurrently with the file-merge/validate/write below --
        # only the actual index rebuild further down needs to lock those out.
        live_path = os.path.join(CHUNKS_DIR, live_filename)
        header, live_blocks, live_order = "", {}, []
        if os.path.exists(live_path):
            with open(live_path, "r", encoding="utf-8") as f:
                header, live_blocks, live_order = _split_raw_chunks(f.read())

        for cid in selected_ids:
            if cid not in live_blocks:
                live_order.append(cid)
            live_blocks[cid] = draft_blocks[cid]

        new_file_text = _render_chunk_file(header, live_blocks, live_order)

        # Validate the merged result BEFORE touching the live file -- a bad
        # promotion should never leave the production chunk file broken.
        tmp_path = live_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(new_file_text)
        validation_warnings = []
        docs = parse_chunk_file(tmp_path, validation_warnings)
        if not docs:
            os.remove(tmp_path)
            raise HTTPException(status_code=500, detail="Promotion would produce an unparseable chunk file — aborted, nothing was changed")

        os.replace(tmp_path, live_path)

        # Full re-ingest (~30-40s across the whole corpus) plus reloading
        # this process's own in-memory index -- see reload_index()'s
        # docstring for why the reload step is required and not optional.
        # Write-locked against _index_lock specifically for this part (not
        # the file I/O above) -- see _IndexRWLock's docstring: this is what
        # actually blocks new /query reads and waits for in-flight ones,
        # since ingest_chunks() deletes the live Chroma collection before
        # rebuilding it.
        _index_lock.acquire_write()
        try:
            ingest_chunks()
            query_module.reload_index()
        finally:
            _index_lock.release_write()

        # Any saved answer that cited one of the chunks we just changed
        # might now be stating an outdated number -- check just those
        # entries (cheap and precise, since we already know exactly which
        # chunk_ids moved) and auto-update or flag them before anyone else
        # sees a stale correction. Doesn't touch the chroma index, so this
        # runs outside the write lock too.
        touched = answer_library.refresh_stale_entries(changed_chunk_ids=set(selected_ids))

        # The same event has to reach the OTHER store too. The library gets
        # entries re-checked and rewritten or flagged above (they're human
        # corrections, worth preserving); the query cache just gets the
        # affected entries dropped, since an unreviewed answer built on
        # superseded chunk content has nothing worth salvaging. Without this
        # the cache kept serving pre-update figures indefinitely -- update a
        # rate, ask the same question, get the old number back from cache.
        invalidated = _invalidate_query_cache_for_chunks(set(selected_ids))

    return PromoteResponse(
        status="promoted",
        lender=lender_code,
        promoted_chunk_ids=selected_ids,
        total_chunks_in_file=len(live_blocks),
        total_chunks_in_index=query_module._chroma_collection.count(),
        answer_library_updates=[
            AnswerLibraryUpdate(id=e["id"], question=e["question"], status=e["status"], note=e.get("note", ""))
            for e in touched
        ],
        query_cache_invalidated=invalidated,
    )
