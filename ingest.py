import re
from pathlib import Path

MIN_CHARS = 300
MAX_CHARS = 500
OVERLAP = 75


def _split_text(text: str):
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []
    # Split on sentence boundaries and line breaks when possible
    pieces = re.split(r'(?<=[.!?])\s+|\n+', text)
    pieces = [piece.strip() for piece in pieces if piece.strip()]
    return pieces


def _make_chunks(text: str, source: str):
    pieces = _split_text(text)
    chunks = []
    current = ""

    def _finish_chunk(current_chunk):
        chunk_text = current_chunk.strip()
        if not chunk_text:
            return None
        return chunk_text

    for piece in pieces:
        if not current:
            current = piece
        elif len(current) + 1 + len(piece) <= MAX_CHARS:
            current = f"{current} {piece}"
        else:
            finished = _finish_chunk(current)
            if finished:
                chunks.append(finished)
            overlap_text = finished[-OVERLAP:] if finished and len(finished) > OVERLAP else finished
            current = f"{overlap_text} {piece}".strip() if overlap_text else piece

    if current:
        finished = _finish_chunk(current)
        if finished:
            chunks.append(finished)

    adjusted = []
    for chunk in chunks:
        if len(chunk) > MAX_CHARS:
            start = 0
            while start < len(chunk):
                end = min(len(chunk), start + MAX_CHARS)
                adjusted.append(chunk[start:end].strip())
                start = end - OVERLAP if end - OVERLAP > start else end
        else:
            adjusted.append(chunk)

    return adjusted


def get_chunks():
    documents_dir = Path("documents")
    chunks = []
    for path in sorted(documents_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        source = path.name
        piece_chunks = _make_chunks(text, source)
        for idx, chunk in enumerate(piece_chunks):
            chunk_text = chunk.strip()
            if not chunk_text:
                continue
            chunks.append({"text": chunk_text, "source": source, "chunk_index": idx})
    return chunks


if __name__ == "__main__":
    all_chunks = get_chunks()
    print(f"Loaded {len(all_chunks)} chunks from documents.")
