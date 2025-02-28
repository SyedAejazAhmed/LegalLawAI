import faiss
import json
import ollama
import numpy as np
from sentence_transformers import SentenceTransformer

# ✅ Paths to FAISS index and metadata
faiss_index_path = "pdf_to_text/faiss_index.faiss"
metadata_path = "pdf_to_text/faiss_metadata.json"

# ✅ Load FAISS index
index = faiss.read_index(faiss_index_path)

# ✅ Load metadata mapping FAISS IDs to legal text
with open(metadata_path, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# ✅ Load embedding model (Must be the same model used for FAISS indexing)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_legal_text(query, top_k=3, max_tokens=500):
    """Retrieves the most relevant legal text sections using FAISS."""
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)  # Generate query embedding
    _, indices = index.search(query_embedding, top_k)  # Retrieve top-k results

    results = []
    for idx in indices[0]:
        if idx < len(metadata):
            text = metadata[idx]["text"]
            if len(text.split()) > max_tokens:
                text = " ".join(text.split()[:max_tokens])
            results.append(text)

    return results

def query_deepseek_r1(query):
    """Retrieves legal text and queries DeepSeek-R1 with streaming enabled."""
    retrieved_texts = retrieve_legal_text(query)
    
    if not retrieved_texts:
        return "No relevant legal text found."

    # ✅ Use only the top 2 relevant sections
    context = "\n\n".join(retrieved_texts[:2])  

    prompt = f"""
    You are a legal AI assistant. Answer the following legal query based on the retrieved legal texts.
    
    **Query:** {query}
    
    **Relevant Legal Sections:**
    {context}
    
    Provide a clear and concise legal explanation.
    """

    # ✅ Enable streaming for faster response display
    response = ollama.chat(
        model="deepseek-r1:1.5b",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.7, "max_tokens": 200},  # Limit response length
        stream=True  # ✅ Stream response token-by-token
    )

    # ✅ Display response in real-time
    full_response = ""
    for chunk in response:
        print(chunk["message"]["content"], end="", flush=True)  # Print as it's generated
        full_response += chunk["message"]["content"]

    return full_response

# ✅ Example Query
query = input("\nEnter the Query: ")
response = query_deepseek_r1(query)

print("\n\n🔹 Answer from DeepSeek-R1 🔹")
print(response)