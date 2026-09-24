import os
import sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import chromadb
from src.config import CHUNKS_DIR, CHROMA_DIR, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

# Must stay in sync with LENDER_KEYWORDS / INTENT_KEYWORDS keys in src/query.py.
# A typo'd lenders/intent value in a chunk file doesn't raise an error on its
# own — ChromaDB will happily store any string — it just silently breaks
# metadata-filtered retrieval for that one chunk. Validating against this
# known-good set catches that at ingest time instead of a broker getting a
# wrong answer weeks later.
VALID_LENDERS = {"WESTPAC", "BFS", "RESIMAC", "CFAL", "ANGLE", "FLEXI", "METRO"}
VALID_INTENTS = {
    "PRICING", "ELIGIBILITY", "LOAN_LIMITS", "DOCUMENTATION", "FEES",
    "SETTLEMENT", "EXCLUSIONS", "SPECIAL_PROGRAMS", "ASSET_ELIGIBILITY",
    "MEDICAL_PROGRAMS", "ROLLOVER_REPLACEMENT",
}


def split_chunk_blocks(content: str, warnings: list = None):
    """Split one chunk file's raw text on the '## chunk_id: ...' / '\\n---\\n'
    convention every chunk file shares. Returns (header, {chunk_id:
    raw_block_text}, [chunk_id order]).

    This is the one place that knows this format's splitting rules --
    parse_chunk_file() (below), get_all_chunk_blocks(), and src.api's
    /chunks/draft+/chunks/promote merge logic all build on this instead of
    each re-implementing the same regex. Three near-identical copies of this
    used to exist; if the delimiter/marker format ever changes, there used
    to be a real risk of updating only some of them, silently desyncing
    what different parts of the pipeline consider a valid chunk boundary.

    `warnings` (optional) collects a note when a '## chunk_id:' marker is
    found but its ID can't be parsed out, rather than silently dropping
    that section.
    """
    if warnings is None:
        warnings = []
    parts = re.split(r'\n---\n', content)
    header = ""
    blocks = {}
    order = []
    seen_chunk = False
    for part in parts:
        if '## chunk_id:' not in part:
            if not seen_chunk:
                header = part
            continue
        match = re.search(r'## chunk_id:\s*(\S+)', part)
        if not match:
            warnings.append(f"found a '## chunk_id:' marker but couldn't parse an ID from it — section skipped: {part[:80]!r}...")
            continue
        seen_chunk = True
        chunk_id = match.group(1).strip()
        blocks[chunk_id] = part.strip("\n")
        order.append(chunk_id)
    return header, blocks, order


def parse_chunk_file(filepath, warnings=None):
    """Parse a markdown chunk file into a list of Document objects.

    `warnings` (optional list) collects human-readable problems found along
    the way instead of silently skipping them — a malformed or mistagged
    chunk otherwise vanishes with no trace beyond a lower total chunk count.
    """
    if warnings is None:
        warnings = []
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    split_warnings = []
    _, raw_blocks, chunk_order = split_chunk_blocks(content, split_warnings)
    for w in split_warnings:
        warnings.append(f"{filename}: {w}")
    documents = []

    for chunk_id in chunk_order:
        raw = raw_blocks[chunk_id]

        # Extract metadata fields
        def get_field(field_name):
            pattern = rf'\*\*{field_name}:\*\*\s*(.+?)(?:\n|$)'
            match = re.search(pattern, raw)
            return match.group(1).strip() if match else ""

        lenders = get_field("lenders")
        intent = get_field("intent")
        borrower_profile = get_field("borrower_profile")
        asset_class = get_field("asset_class")
        doc_type = get_field("doc_type")
        loan_size_band = get_field("loan_size_band")
        answerable_questions = get_field("answerable_questions")
        trigger_words = get_field("trigger_words")
        confidence = get_field("confidence")
        last_verified = get_field("last_verified")
        policy_fields = get_field("policy_fields")
        source = get_field("source")

        # Extract content (everything after **Content:**)
        content_match = re.search(r'\*\*Content:\*\*\s*\n(.*?)(?=\n---|\Z)', raw, re.DOTALL)
        if not content_match:
            warnings.append(f"{filename}: chunk_id '{chunk_id}' has no '**Content:**' section — chunk skipped entirely")
            continue
        chunk_content = content_match.group(1).strip()

        if not chunk_content:
            warnings.append(f"{filename}: chunk_id '{chunk_id}' has an empty Content section")
        if not lenders:
            warnings.append(f"{filename}: chunk_id '{chunk_id}' has no lenders field — will never be retrieved by lender-scoped search")
        elif lenders not in VALID_LENDERS:
            warnings.append(f"{filename}: chunk_id '{chunk_id}' has lenders='{lenders}', not one of {sorted(VALID_LENDERS)} — check for a typo")
        if not intent:
            warnings.append(f"{filename}: chunk_id '{chunk_id}' has no intent field — will only surface via lender-only search, never lender+intent")
        elif intent not in VALID_INTENTS:
            warnings.append(f"{filename}: chunk_id '{chunk_id}' has intent='{intent}', not one of {sorted(VALID_INTENTS)} — check for a typo")

        # Build enriched text for embedding
        # Prepend answerable_questions and trigger_words so the
        # embedding model learns to associate these terms with the chunk
        enriched_text = f"""Questions this chunk answers: {answerable_questions}
Key terms: {trigger_words}

{chunk_content}"""

        # Build metadata dict for ChromaDB filtering
        metadata = {
            "chunk_id": chunk_id,
            "lenders": lenders,
            "topic_intent": intent,
            "borrower_profile": borrower_profile,
            "asset_class": asset_class,
            "doc_type": doc_type,
            "loan_size_band": loan_size_band,
            "answerable_questions": answerable_questions,
            "confidence": confidence,
            "last_verified": last_verified,
            "policy_fields": policy_fields,
            "source": source,
            "file_name": filename
        }

        documents.append(Document(
            text=enriched_text,
            metadata=metadata,
            id_=chunk_id
        ))

    return documents


def get_all_chunk_blocks() -> dict:
    """Flat {chunk_id: raw_markdown_block} across every file in CHUNKS_DIR --
    the raw '## chunk_id: ...' section text, not the Document objects
    parse_chunk_file returns (those hold the embedding-ready enriched text,
    not the original block). Used by the answer library's staleness check
    to snapshot/compare a chunk's exact content over time, independent of
    which physical file it lives in."""
    blocks = {}
    chunk_files = [f for f in os.listdir(CHUNKS_DIR) if f.endswith('.md')]
    for filename in sorted(chunk_files):
        with open(os.path.join(CHUNKS_DIR, filename), "r", encoding="utf-8") as f:
            content = f.read()
        _, file_blocks, _ = split_chunk_blocks(content)
        blocks.update(file_blocks)
    return blocks


def ingest_chunks():
    print("Parsing chunk files...")
    all_documents = []
    warnings = []

    chunk_files = [f for f in os.listdir(CHUNKS_DIR) if f.endswith('.md')]
    for filename in sorted(chunk_files):
        filepath = os.path.join(CHUNKS_DIR, filename)
        docs = parse_chunk_file(filepath, warnings)
        print(f"  {filename}: {len(docs)} chunks parsed")
        all_documents.extend(docs)

    print(f"\nTotal chunks: {len(all_documents)}")

    # Duplicate chunk_ids silently overwrite each other in ChromaDB (id_ is
    # the primary key) — one of the two chunks would simply never be
    # retrievable, with no error at ingest time to explain why.
    seen_ids = {}
    for doc in all_documents:
        cid = doc.metadata["chunk_id"]
        if cid in seen_ids:
            warnings.append(f"Duplicate chunk_id '{cid}' in {seen_ids[cid]} and {doc.metadata['file_name']} — one will silently overwrite the other")
        else:
            seen_ids[cid] = doc.metadata["file_name"]

    if warnings:
        print(f"\n{len(warnings)} WARNING(S):")
        for w in warnings:
            print(f"  ! {w}")
    else:
        print("\nNo validation warnings — all chunk_ids unique, all lenders/intent values recognised.")

    print("\nSetting up embedding model...")
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
    Settings.embed_model = embed_model
    Settings.llm = None

    print("Setting up ChromaDB...")
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete and recreate the policy chunks collection
    try:
        chroma_client.delete_collection("lifex_policies")
        print("Deleted old collection")
    except:
        pass

    chroma_collection = chroma_client.get_or_create_collection("lifex_policies")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Embedding and storing chunks...")
    splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    index = VectorStoreIndex.from_documents(
        all_documents,
        storage_context=storage_context,
        transformations=[splitter],
        show_progress=True
    )

    final_count = chroma_collection.count()
    print(f"\nDone. {final_count} chunks stored in ChromaDB.")

    # Verify a sample
    print("\nSample verification — checking metadata on first 3 stored chunks:")
    sample = chroma_collection.get(limit=3, include=["metadatas"])
    for i, meta in enumerate(sample["metadatas"]):
        print(f"  [{i+1}] chunk_id: {meta.get('chunk_id')} | "
              f"lender: {meta.get('lenders')} | "
              f"intent: {meta.get('topic_intent')}")

    return index


if __name__ == "__main__":
    ingest_chunks()