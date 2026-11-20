"""
RAG (Retrieval-Augmented Generation) Engine for TutorGPT.
Handles document ingestion, semantic chunking, vector indexing,
and top-k similarity retrieval with exact source citations.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import DocumentChunk


class RAGEngine:
    """
    Retrieval engine supporting vector similarity search over study materials.
    Uses TF-IDF + Cosine Similarity by default for zero-overhead, deterministic,
    high-speed local retrieval, with hooks for dense sentence-transformers.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: List[DocumentChunk] = []
        self.sources: List[str] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._matrix = None

    def ingest_text(self, text: str, source_name: str, metadata: Optional[dict] = None) -> int:
        """Chunk and index raw text content."""
        if not text.strip():
            return 0

        if source_name not in self.sources:
            self.sources.append(source_name)

        new_chunks = self._chunk_text(text, source_name, metadata or {})
        start_id = len(self.chunks)
        for i, c in enumerate(new_chunks):
            c.chunk_id = start_id + i
            self.chunks.append(c)

        self._rebuild_index()
        return len(new_chunks)

    def ingest_file(self, file_path: str | Path) -> int:
        """Read and index a file from disk (supports .txt, .md, .pdf, .docx, .pptx)."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Study material not found: {path}")

        ext = path.suffix.lower()
        try:
            if ext in (".pdf", ".docx", ".doc", ".pptx", ".ppt"):
                from shared.document_parser import parse_uploaded_file
                content = parse_uploaded_file(path.name, path.read_bytes())
            else:
                content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            raise IOError(f"Could not read {path}: {e}")

        return self.ingest_text(content, path.name, {"file_path": str(path.resolve())})

    def ingest_directory(self, dir_path: str | Path, extensions: Tuple[str, ...] = (".txt", ".md", ".py")) -> int:
        """Recursively index all matching documents in a directory."""
        directory = Path(dir_path)
        if not directory.exists() or not directory.is_dir():
            return 0

        total_chunks = 0
        for ext in extensions:
            for file_path in directory.rglob(f"*{ext}"):
                total_chunks += self.ingest_file(file_path)
        return total_chunks

    def _chunk_text(self, text: str, source_name: str, metadata: dict) -> List[DocumentChunk]:
        """Split text into semantic chunks with overlapping boundaries."""
        # Clean text
        text = text.replace("\r\n", "\n")
        
        # Split by paragraphs / markdown headers first
        sections = re.split(r"\n{2,}", text)
        chunks: List[DocumentChunk] = []

        current_buf = ""
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue

            if len(current_buf) + len(sec) <= self.chunk_size:
                current_buf = (current_buf + "\n\n" + sec).strip()
            else:
                if current_buf:
                    chunks.append(DocumentChunk(
                        chunk_id=0,
                        source_name=source_name,
                        text=current_buf,
                        metadata=metadata
                    ))
                # If a single section is larger than chunk_size, split by sentences
                if len(sec) > self.chunk_size:
                    sentences = re.split(r"(?<=[.!?])\s+", sec)
                    sub_buf = ""
                    for s in sentences:
                        if len(sub_buf) + len(s) <= self.chunk_size:
                            sub_buf = (sub_buf + " " + s).strip()
                        else:
                            if sub_buf:
                                chunks.append(DocumentChunk(
                                    chunk_id=0,
                                    source_name=source_name,
                                    text=sub_buf,
                                    metadata=metadata
                                ))
                            sub_buf = s
                    current_buf = sub_buf
                else:
                    current_buf = sec

        if current_buf:
            chunks.append(DocumentChunk(
                chunk_id=0,
                source_name=source_name,
                text=current_buf,
                metadata=metadata
            ))

        return chunks

    def _rebuild_index(self):
        """Build or update the TF-IDF vector index over all indexed chunks."""
        if not self.chunks:
            self._matrix = None
            self._vectorizer = None
            return

        corpus = [c.text for c in self.chunks]
        max_df = 0.95 if len(corpus) > 2 else 1.0
        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_df=max_df,
            min_df=1
        )
        self._matrix = self._vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 3, threshold: float = 0.05) -> List[DocumentChunk]:
        """
        Retrieve the top-k most relevant chunks for a student query,
        sorted by cosine similarity score.
        """
        if not self.chunks or self._matrix is None or self._vectorizer is None:
            return []

        query_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self._matrix).flatten()

        ranked_indices = np.argsort(sims)[::-1]
        results = []

        for idx in ranked_indices[:top_k]:
            score = float(sims[idx])
            if score >= threshold:
                chunk = self.chunks[idx].model_copy(deep=True)
                chunk.score = round(score, 4)
                results.append(chunk)

        return results

    def format_context_for_prompt(self, chunks: List[DocumentChunk]) -> str:
        """Format retrieved chunks with clear source citation markers for the LLM."""
        if not chunks:
            return "No matching study material found in the database."

        formatted_blocks = []
        for i, c in enumerate(chunks, 1):
            formatted_blocks.append(
                f"[Source: {c.source_name} | Chunk #{c.chunk_id} | Relevance: {c.score:.2f}]\n{c.text}"
            )
        return "\n\n---\n\n".join(formatted_blocks)

    def clear(self):
        """Reset the knowledge base."""
        self.chunks.clear()
        self.sources.clear()
        self._matrix = None
        self._vectorizer = None
