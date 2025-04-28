# -*- coding: utf-8 -*-
# filename: agents/resume_agent.py

import os
import time
import fitz  # PyMuPDF for PDF processing
from typing import List, Dict, Any

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec, Index
from sentence_transformers import SentenceTransformer

# -------------------------------
# Configuration
# -------------------------------
PINECONE_API_KEY   = os.getenv("PINECONE_API_KEY", "pcsk_3TLJGv_9pf4XQHz3Gv6AUKQyk1vNwkUnCHz8WkcNj9cpa1PFWEtguEWQPpVprZyXyF6khn")
INDEX_NAME         = os.getenv("PINECONE_INDEX_NAME", "resume-index")
EMBEDDING_MODEL    = "sentence-transformers/all-mpnet-base-v2"
DIMENSION          = 768
CHUNK_SIZE         = 1000
CHUNK_OVERLAP      = 150
BATCH_SIZE         = 32
TOP_K              = 10  # default retrieval size

# -------------------------------
# Initialize Pinecone + Embedder
# -------------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)

existing = [info["name"] for info in pc.list_indexes().indexes]
if INDEX_NAME not in existing:
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    time.sleep(15)

index: Index = pc.Index(INDEX_NAME)

device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
embedder = SentenceTransformer(EMBEDDING_MODEL, device=device)

# -------------------------------
# PDF → Text → Chunks
# -------------------------------
def load_and_chunk_pdf_text(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Resume not found: {path}")

    doc = fitz.open(path)
    docs: List[Document] = []
    for i in range(len(doc)):
        text = doc.load_page(i).get_text("text").strip()
        if not text:
            continue
        docs.append(Document(
            page_content=text,
            metadata={"source": os.path.basename(path), "page": i + 1}
        ))
    doc.close()

    if not docs:
        raise ValueError("No extractable text found in PDF.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)

    formatted = []
    for idx, chunk in enumerate(chunks):
        txt = chunk.page_content.strip()
        if len(txt) < 50:
            continue
        formatted.append({
            "id": f"{chunk.metadata['source']}-chunk-{idx}",
            "text": txt,
            "metadata": chunk.metadata
        })
    return formatted

# -------------------------------
# Upsert with metadata["text"]
# -------------------------------
def upsert_to_pinecone(index: Index, chunks: List[Dict[str, Any]]):
    batch = []
    for chunk in chunks:
        vec = embedder.encode([chunk["text"]], convert_to_numpy=True)[0].tolist()
        meta = {**chunk["metadata"], "text": chunk["text"]}
        batch.append({
            "id": chunk["id"],
            "values": vec,
            "metadata": meta
        })
        if len(batch) >= BATCH_SIZE:
            index.upsert(vectors=batch)
            batch = []
    if batch:
        index.upsert(vectors=batch)

# -------------------------------
# Retriever with per-resume filter
# -------------------------------
class PineconeRetriever:
    def __init__(self, index: Index, embedder: SentenceTransformer, source: str):
        """
        source: the basename of the resume file, e.g. "Shaikh_CV.pdf"
        """
        self.index = index
        self.embedder = embedder
        # filter to only return vectors whose metadata.source matches this resume
        self.filter = {"source": source}

    def retrieve(self, query: str, top_k: int = TOP_K) -> str:
        qvec = self.embedder.encode([query], convert_to_numpy=True)[0].tolist()
        res = self.index.query(
            vector=qvec,
            top_k=top_k,
            include_metadata=True,
            filter=self.filter
        )
        texts = [m.metadata.get("text", "") for m in res.matches]
        return "\n\n---\n\n".join(texts)
