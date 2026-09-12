import time
import uuid
import json
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from agent import run_agent, AgentResponseSchema
from guardrails import mask_pii
from rag_core import COLL_SENTENCE, sentence_chunker

app = FastAPI(title="Cred Support Agent API", version="1.0.0")

class AskRequest(BaseModel):
    query: str = Field(..., example="What are the KYC requirements for a personal loan?")
    thread_id: Optional[str] = Field(default="default_session", example="user_session_123")

class AddDocumentRequest(BaseModel):
    doc_id: str = Field(..., example="DOC-013")
    topic: str = Field(..., example="credit_limit_enhancement")
    title: str = Field(..., example="Credit Limit Enhancement Policy")
    content: str = Field(..., example="Credit limit enhancement eligibility requires 12 months of clean repayment history.")

LOG_FILE = "api_requests.jsonl"

@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    start_time = time.time()
    trace_id = str(uuid.uuid4())
    
    # Process request
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    
    # Read and mask PII from query parameters or URL if present
    masked_path, _ = mask_pii(request.url.path)
    
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "trace_id": trace_id,
        "method": request.method,
        "path": masked_path,
        "status_code": response.status_code,
        "duration_ms": duration_ms
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
        
    return response

@app.post("/ask", response_model=AgentResponseSchema)
def ask_endpoint(req: AskRequest):
    # Mask query before writing to log
    masked_query, _ = mask_pii(req.query)
    
    # Log specific request entry with masked query
    log_entry = {
        "trace_id": str(uuid.uuid4()),
        "endpoint": "/ask",
        "masked_query": masked_query,
        "thread_id": req.thread_id
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
        
    res = run_agent(req.query, thread_id=req.thread_id)
    return res

@app.post("/add-document")
def add_document_endpoint(req: AddDocumentRequest):
    chunks = sentence_chunker(req.content)
    ids, docs, metas = [], [], []
    for idx, c in enumerate(chunks):
        ids.append(f"{req.doc_id}_{idx}")
        docs.append(c)
        metas.append({"doc_id": req.doc_id, "topic": req.topic, "title": req.title})
        
    COLL_SENTENCE.add(documents=docs, metadatas=metas, ids=ids)
    
    return {
        "status": "success",
        "doc_id": req.doc_id,
        "chunks_indexed": len(chunks),
        "message": f"Document '{req.title}' successfully indexed into Knowledge Base."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)