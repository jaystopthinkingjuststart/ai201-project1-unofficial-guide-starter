"""
ingest.py — Milestone 3: load, clean, and chunk the Unofficial Guide corpus.

Run:  python ingest.py
Prints one cleaned document, the total chunk count, and 5 spread-out sample
chunks so you can do the Milestone 3 inspection checkpoint.

Chunking spec (from planning.md):
  - 400-character sliding window, 50-character overlap
  - review-heavy corpus: one chunk ≈ one self-contained opinion
"""

import os
import re
import html
import glob

DOCUMENTS_DIR = "documents"
CHUNK_SIZE = 400        # characters — window size for the long-comment fallback
OVERLAP = 50            # characters — overlap used only when windowing a long comment
MIN_CHUNK_LEN = 50      # min length for a windowed piece
MAX_CHUNK_LEN = 600     # a single comment longer than this gets windowed
PARAGRAPH_MIN_LEN = 12  # drop sub-fragments below this (after dropping single-token lines)


def load_documents():
    """Read every .txt file in documents/. Returns a list of {source, text} dicts.

    The filename (without .txt) becomes the `source` label, so name your files
    descriptively (e.g. rmp_jane_doe_coms227.txt) — that label is what gets
    prepended to each chunk for attribution.
    """
    docs = []
    paths = sorted(glob.glob(os.path.join(DOCUMENTS_DIR, "*.txt")))
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        source = os.path.splitext(os.path.basename(path))[0]
        docs.append({"source": source, "text": text})
    print(f"Loaded {len(docs)} document(s): {[d['source'] for d in docs]}")
    return docs


def clean_text(text):
    """Strip HTML, decode entities, drop common Reddit/RMP boilerplate, tidy whitespace.

    NOTE: the boilerplate patterns below are a starting point. After you paste
    real text in, read a cleaned doc and ADD patterns for whatever cruft is left
    (every site copy-pastes differently). Cleaning is corpus-specific.
    """
    # 1. Decode HTML entities left from copy-paste: &amp;  &nbsp;  &#39;
    text = html.unescape(text)
    # 2. Remove any literal HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # 3. Remove common forum / Rate My Professors UI boilerplate lines.
    #    Tuned to the artifacts seen in THIS corpus (Reddit + RMP copy-paste).
    boilerplate = [
        r"(?im)^\s*(reply|share|report|save|award|follow|give award)\s*$",
        r"(?im)^\s*\d+\s*(points?|comments?|upvotes?|awards?)\s*$",
        # Reddit timestamps: "2y ago", "6 yr ago", "1mo ago", "· 3d ago ·"
        r"(?im)^\s*·?\s*\d+\s*(y|yr|mo|wk|d|day|hr|h|min|m|sec|s)s?\.?\s*ago\s*·?\s*$",
        r"(?im)^\s*u/\S+\s+avatar\s*$",          # "u/veto001 avatar"
        r"(?im)^\s*•\s*$",                        # bullet separators
        r"(?im)^\s*\d+\s*more\s+repl(?:y|ies)\s*$",  # "4 more replies"
        r"(?im)^\s*comments?\s+section\s*$",      # "Comments Section"
        r"(?im)^\s*this rating has been reported.*$",  # RMP report banner
        r"(?im)^\s*[A-Z][a-z]{2}\s+\d{1,2}(st|nd|rd|th)?,?\s+\d{4}\s*$",  # "Dec 7th, 2025"
        r"(?im)^\s*(quality|difficulty|would take again|level of difficulty|for credit|attendance|grade received|textbook)\s*:?.*$",
        r"(?im)^\s*read more\s*$",
        r"(?im)^\s*\d+\s*$",  # stray vote/count numbers on their own line
    ]
    for pat in boilerplate:
        text = re.sub(pat, "", text)
    # 4. Collapse runs of spaces and blank lines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def _window(text, size, overlap):
    """Sliding-window fallback for a single comment longer than MAX_CHUNK_LEN."""
    pieces = []
    start = 0
    while start < len(text):
        piece = text[start:start + size].strip()
        if len(piece) >= MIN_CHUNK_LEN:
            pieces.append(piece)
        start += size - overlap
    return pieces


def chunk_document(text, source):
    """Boundary-based chunking: one chunk per review/comment.

    Comments are separated by blank lines in the cleaned text, so we split on
    those boundaries — each chunk is one self-contained opinion. Single-token
    lines (usernames, "[deleted]", stray dots) and tiny fragments are dropped.
    A comment longer than MAX_CHUNK_LEN falls back to a sliding window so no
    single chunk gets huge. Each chunk is prefixed with its source label so the
    professor/course/topic travels with the text.
    """
    units = re.split(r"\n\s*\n", text)
    chunks = []
    counter = 0
    for unit in units:
        unit = " ".join(unit.split())          # flatten internal newlines, tidy spaces
        if " " not in unit or len(unit) < PARAGRAPH_MIN_LEN:
            continue                            # drop usernames / fragments
        pieces = [unit] if len(unit) <= MAX_CHUNK_LEN else _window(unit, CHUNK_SIZE, OVERLAP)
        for piece in pieces:
            chunks.append({
                "text": f"[{source}] {piece}",
                "source": source,
                "chunk_id": f"{source}_{counter}",
            })
            counter += 1
    return chunks


def build_chunks():
    """Load -> clean -> chunk every document. Returns the full list of chunks."""
    docs = load_documents()
    all_chunks = []
    for doc in docs:
        cleaned = clean_text(doc["text"])
        all_chunks.extend(chunk_document(cleaned, doc["source"]))
    return all_chunks


if __name__ == "__main__":
    docs = load_documents()
    if not docs:
        print(f"\nNo .txt files found in {DOCUMENTS_DIR}/. Collect documents first.")
        raise SystemExit

    # --- Cleaning inspection: read one full cleaned document ---
    print("\n" + "=" * 60)
    print(f"CLEANED DOCUMENT: {docs[0]['source']}")
    print("=" * 60)
    print(clean_text(docs[0]["text"])[:1500])

    # --- Chunk + count ---
    chunks = build_chunks()
    print("\n" + "=" * 60)
    print(f"TOTAL CHUNKS: {len(chunks)}")
    print("=" * 60)

    # --- 5 chunks spread across the corpus (not just the first 5) ---
    step = max(1, len(chunks) // 5)
    print("\n--- 5 sample chunks ---")
    for c in chunks[::step][:5]:
        print(f"\n[{c['chunk_id']}] ({len(c['text'])} chars)\n{c['text']}")
