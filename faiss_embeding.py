import os
import json
import torch
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import warnings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ✅ Load Faster Model (MiniLM) for embedding
device = "cpu"  # Force CPU usage
model = SentenceTransformer("all-MiniLM-L6-v2").to(device)

warnings.filterwarnings("ignore", category=FutureWarning)

# ✅ Paths
input_json_path = "pdf_to_text/Laws_structured.json"  # Processed legal text
faiss_index_path = "pdf_to_text/faiss_index.faiss"  # FAISS index storage
metadata_path = "pdf_to_text/faiss_metadata.json"  # JSON metadata storage

# ✅ Initialize FAISS index (HNSW for faster retrieval)
embedding_dim = 384  # MiniLM output size
index = faiss.IndexHNSWFlat(embedding_dim, 32)  # HNSW (Hierarchical Navigable Small World)

metadata = []  # Store metadata (FAISS ID → Chunk Text)
doc_id = 0  # Unique ID for each chunk

# ✅ Define Chunking Parameters
chunk_size = 200  # 200 words per chunk
chunk_overlap = 50  # 50-word overlap
text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

# ✅ Load Extracted Legal Text
with open(input_json_path, "r", encoding="utf-8") as f:
    laws_data = json.load(f)

for law_name, chapters in laws_data.items():
    print(f"📖 Processing {law_name}...")

    for chapter_name, chapter_content in chapters.items():
        # ✅ Split chapter text into overlapping chunks
        text_chunks = text_splitter.split_text(chapter_content)

        # ✅ Generate embeddings for each chunk
        embeddings = model.encode(text_chunks, batch_size=16, convert_to_numpy=True)

        # ✅ Add embeddings to FAISS index
        index.add(embeddings)

        # ✅ Store metadata (FAISS ID → Chunk Text)
        for chunk in text_chunks:
            if chunk.strip():  # Avoid empty chunks
                metadata.append({
                    "id": doc_id,
                    "law": law_name,
                    "chapter": chapter_name,
                    "text": chunk.strip()
                })
                doc_id += 1

# ✅ Save FAISS index
faiss.write_index(index, faiss_index_path)

# ✅ Save metadata as JSON
with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4, ensure_ascii=False)

print(f"✅ FAISS index saved at: {faiss_index_path}")
print(f"✅ Metadata saved at: {metadata_path}")
