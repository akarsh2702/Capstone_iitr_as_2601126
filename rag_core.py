import os
import re
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.utils import embedding_functions
from knowledge_base import KNOWLEDGE_BASE_DOCUMENTS

# Local vector DB initialization
CHROMA_CLIENT = chromadb.Client()
EMBEDDING_FN = embedding_functions.DefaultEmbeddingFunction() # Free, lightweight transformer/onnx

# Collection 1: Fixed-Size Chunking (Size 200 chars, Overlap 40 chars)
COLL_FIXED = CHROMA_CLIENT.get_or_create_collection(
    name="cred_kb_fixed_size",
    embedding_function=EMBEDDING_FN
)

# Collection 2: Sentence-Based Chunking
COLL_SENTENCE = CHROMA_CLIENT.get_or_create_collection(
    name="cred_kb_sentence_based",
    embedding_function=EMBEDDING_FN
)

def fixed_size_chunker(text: str, chunk_size: int = 200, overlap: int = 40) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += (chunk_size - overlap)
    return chunks

def sentence_chunker(text: str) -> List[str]:
    # Regex split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def index_knowledge_base():
    # Index Fixed-Size
    fixed_docs, fixed_metas, fixed_ids = [], [], []
    fixed_idx = 0
    for doc in KNOWLEDGE_BASE_DOCUMENTS:
        chunks = fixed_size_chunker(doc["content"])
        for chunk in chunks:
            fixed_ids.append(f"fixed_{fixed_idx}")
            fixed_docs.append(chunk)
            fixed_metas.append({"doc_id": doc["doc_id"], "topic": doc["topic"], "title": doc["title"]})
            fixed_idx += 1
            
    COLL_FIXED.add(documents=fixed_docs, metadatas=fixed_metas, ids=fixed_ids)
    
    # Index Sentence-Based
    sent_docs, sent_metas, sent_ids = [], [], []
    sent_idx = 0
    for doc in KNOWLEDGE_BASE_DOCUMENTS:
        chunks = sentence_chunker(doc["content"])
        for chunk in chunks:
            sent_ids.append(f"sent_{sent_idx}")
            sent_docs.append(chunk)
            sent_metas.append({"doc_id": doc["doc_id"], "topic": doc["topic"], "title": doc["title"]})
            sent_idx += 1
            
    COLL_SENTENCE.add(documents=sent_docs, metadatas=sent_metas, ids=sent_ids)

# Calibrated similarity threshold from empirical tuning
SIMILARITY_THRESHOLD = 0.550

def query_rag(query: str, collection_type: str = "sentence", top_k: int = 3) -> Tuple[List[Dict[str, Any]], bool]:
    collection = COLL_SENTENCE if collection_type == "sentence" else COLL_FIXED
    results = collection.query(query_texts=[query], n_results=top_k)
    
    retrieved_chunks = []
    if not results or not results["documents"] or not results["documents"][0]:
        return [], False
        
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0]*len(documents)
    
    is_supported = False
    for doc_text, meta, dist in zip(documents, metadatas, distances):
        # Convert Chroma distance to cosine similarity approximation (1 - norm_dist)
        sim_score = max(0.0, 1.0 - (dist / 2.0))
        if sim_score >= SIMILARITY_THRESHOLD:
            is_supported = True
        retrieved_chunks.append({
            "chunk_text": doc_text,
            "metadata": meta,
            "similarity_score": round(sim_score, 4)
        })
        
    return retrieved_chunks, is_supported

def generate_grounded_answer(query: str, collection_type: str = "sentence") -> Dict[str, Any]:
    chunks, is_supported = query_rag(query, collection_type=collection_type, top_k=3)
    
    if not is_supported or not chunks:
        return {
            "query": query,
            "answer": "I do not have sufficient information in Cred's verified loan policies to answer this question accurately. Please contact Cred support for further assistance.",
            "grounded": False,
            "retrieved_chunks": chunks
        }
        
    context_str = "\n".join([f"- {c['chunk_text']}" for c in chunks])
    
    # Deterministic MOCK_LLM grounded response synthesis
    answer = f"Based on Cred loan policies:\n{context_str}"
    
    return {
        "query": query,
        "answer": answer,
        "grounded": True,
        "retrieved_chunks": chunks
    }

# Initialize DB on load
index_knowledge_base()

if __name__ == "__main__":
    print("--- TESTING GROUNDED GENERATION & CALIBRATED FALLBACK ---")
    in_scope_test = "What is the minimum credit score required for a home loan?"
    out_scope_test = "What is the best recipe for baking sourdough bread?"
    
    print("\nIn-Scope Result:")
    res_in = generate_grounded_answer(in_scope_test)
    print(f"Grounded: {res_in['grounded']}")
    print(f"Answer: {res_in['answer']}")
    
    print("\nOut-of-Scope Result:")
    res_out = generate_grounded_answer(out_scope_test)
    print(f"Grounded: {res_out['grounded']}")
    print(f"Answer: {res_out['answer']}")