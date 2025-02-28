import faiss
import json
import ollama
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import torch
from sentence_transformers import SentenceTransformer
import logging
from django.shortcuts import render

def chatbot_ui(request):
    """Renders the chatbot frontend."""
    return render(request, "chatbot/index.html")


# ✅ Set up logging for debugging errors
logging.basicConfig(level=logging.INFO)

# ✅ Paths to FAISS index and metadata
faiss_index_path = "pdf_to_text/faiss_index.faiss"
metadata_path = "pdf_to_text/faiss_metadata.json"

# ✅ Load FAISS index
try:
    index = faiss.read_index(faiss_index_path)
except Exception as e:
    logging.error(f"Error loading FAISS index: {e}")
    index = None  # Prevent crashes

# ✅ Load metadata mapping FAISS IDs to legal text
try:
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
except Exception as e:
    logging.error(f"Error loading metadata: {e}")
    metadata = []

# ✅ Load embedding model (Must be the same model used for FAISS indexing)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_legal_text(query, top_k=3, max_tokens=500):
    """Retrieves the most relevant legal text sections using FAISS."""
    if index is None:
        logging.error("FAISS index not loaded.")
        return []

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


@csrf_exempt
def query_deepseek_r1(request):
    """Handles API requests for legal queries using FAISS + DeepSeek-R1."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("query", "").strip()

            if not query:
                return JsonResponse({"error": "Query is empty"}, status=400)

            retrieved_texts = retrieve_legal_text(query)

            if not retrieved_texts:
                return JsonResponse({"response": "No relevant legal text found."})

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

            # ✅ Stream and collect response
            full_response = ""
            for chunk in response:
                full_response += chunk["message"]["content"]

            return JsonResponse({"response": full_response})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except Exception as e:
            logging.error(f"Error fetching response: {e}")
            return JsonResponse({"error": "⚠️ Error fetching response"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
