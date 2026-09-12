import os
import json
import sqlite3
from typing import Dict, Any, List, TypedDict, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from rag_core import generate_grounded_answer
from tools import check_loan_application_status
from guardrails import run_input_guardrails

# Pydantic Output Validation Schema (Part 2 Task 9)
class AgentResponseSchema(BaseModel):
    query: str = Field(description="The sanitized input query")
    response: str = Field(description="The agent response body")
    intent: str = Field(description="Routed intent: 'policy_rag', 'status_lookup', or 'guarded_refusal'")
    grounded: bool = Field(description="Whether answer is grounded in retrieved context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")

# Agent State
class AgentState(TypedDict):
    query: str
    thread_id: str
    history: List[Dict[str, str]]
    sanitized_query: str
    intent: str
    tool_result: Dict[str, Any]
    final_response: Dict[str, Any]
    is_guarded: bool

# Node 1: Guardrail & Intent Classification
def input_guardrail_node(state: AgentState) -> AgentState:
    raw_query = state["query"]
    guard_res = run_input_guardrails(raw_query)
    
    state["sanitized_query"] = guard_res["masked_text"]
    
    if not guard_res["is_safe"]:
        state["is_guarded"] = True
        state["intent"] = "guarded_refusal"
        state["final_response"] = {
            "query": raw_query,
            "response": "Security Alert: Request rejected due to potential security or prompt injection violation.",
            "intent": "guarded_refusal",
            "grounded": False,
            "metadata": {"guardrail_triggered": "prompt_injection"}
        }
    else:
        state["is_guarded"] = False
        # Intent classification logic
        query_upper = state["sanitized_query"].upper()
        if "CRD-LN-" in query_upper or "STATUS" in query_upper or "APPLICATION" in query_upper:
            state["intent"] = "status_lookup"
        else:
            state["intent"] = "policy_rag"
            
    return state

# Node 2: Policy RAG Tool Node
def rag_tool_node(state: AgentState) -> AgentState:
    query = state["sanitized_query"]
    rag_res = generate_grounded_answer(query)
    
    state["tool_result"] = rag_res
    state["final_response"] = {
        "query": query,
        "response": rag_res["answer"],
        "intent": "policy_rag",
        "grounded": rag_res["grounded"],
        "metadata": {"retrieved_chunks": rag_res["retrieved_chunks"]}
    }
    return state

# Node 3: Loan Status Lookup Tool Node
def status_lookup_node(state: AgentState) -> AgentState:
    query = state["sanitized_query"]
    # Extract record ID or fallback to query
    import re
    match = re.search(r'CRD-LN-\d+', query.upper())
    record_id = match.group(0) if match else query
    
    tool_res = check_loan_application_status(record_id)
    state["tool_result"] = tool_res
    
    if not tool_res["found"]:
        resp_text = f"Application Status Query: {tool_res['error']}"
    else:
        resp_text = (
            f"Loan Application Status for Record {tool_res['record_id']}:\n"
            f"- Category: {tool_res['category']}\n"
            f"- Status: {tool_res['status']}\n"
            f"- Amount: INR {tool_res['loan_amount_inr']:,}\n"
            f"- Days Since Creation: {tool_res['days_since_created']}\n"
            f"- Flagged for Fraud Review: {tool_res['flagged_for_fraud_review']}\n"
            f"- Designed Escalation Score: {tool_res['escalation_score']} (Escalation Recommended: {tool_res['escalation_recommended']})"
        )
        
    state["final_response"] = {
        "query": query,
        "response": resp_text,
        "intent": "status_lookup",
        "grounded": True,
        "metadata": tool_res
    }
    return state

# Node 4: Format & Schema Validation Node
def response_formatter_node(state: AgentState) -> AgentState:
    res = state["final_response"]
    # Validate against Pydantic schema
    validated = AgentResponseSchema(**res)
    state["final_response"] = validated.model_dump()
    
    # Save to history
    state["history"].append({"user": state["query"], "agent": state["final_response"]["response"]})
    return state

# Router Conditional Edge
def route_intent(state: AgentState) -> Literal["rag_tool_node", "status_lookup_node", "response_formatter_node"]:
    if state["is_guarded"]:
        return "response_formatter_node"
    if state["intent"] == "status_lookup":
        return "status_lookup_node"
    return "rag_tool_node"

# Build LangGraph Graph
builder = StateGraph(AgentState)

builder.add_node("input_guardrail_node", input_guardrail_node)
builder.add_node("rag_tool_node", rag_tool_node)
builder.add_node("status_lookup_node", status_lookup_node)
builder.add_node("response_formatter_node", response_formatter_node)

builder.set_entry_point("input_guardrail_node")

builder.add_conditional_edges(
    "input_guardrail_node",
    route_intent,
    {
        "rag_tool_node": "rag_tool_node",
        "status_lookup_node": "status_lookup_node",
        "response_formatter_node": "response_formatter_node"
    }
)

builder.add_edge("rag_tool_node", "response_formatter_node")
builder.add_edge("status_lookup_node", "response_formatter_node")
builder.add_edge("response_formatter_node", END)

# SQLite Checkpointer Setup (Part 4 Task 15)
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
checkpointer = SqliteSaver(conn)

AGENT_GRAPH = builder.compile(checkpointer=checkpointer)

# Persisted Memory Helper (Part 2 Task 8)
MEMORY_FILE = "agent_memory_store.json"

def load_memory() -> Dict[str, List[Dict[str, str]]]:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(memory_data: Dict[str, List[Dict[str, str]]]):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_data, f, indent=2)

def run_agent(query: str, thread_id: str = "default_session") -> Dict[str, Any]:
    memory = load_memory()
    history = memory.get(thread_id, [])
    
    initial_state: AgentState = {
        "query": query,
        "thread_id": thread_id,
        "history": history,
        "sanitized_query": query,
        "intent": "",
        "tool_result": {},
        "final_response": {},
        "is_guarded": False
    }
    
    config = {"configurable": {"thread_id": thread_id}}
    result_state = AGENT_GRAPH.invoke(initial_state, config=config)
    
    memory[thread_id] = result_state["history"]
    save_memory(memory)
    
    return result_state["final_response"]

if __name__ == "__main__":
    print("--- TESTING LANGGRAPH AGENT WITH MEMORY & ROUTING ---")
    
    # Test Policy Route
    res1 = run_agent("What is the foreclosure fee for a business loan?", thread_id="t1")
    print(f"\n[Turn 1 Intent: {res1['intent']}] -> Response:\n{res1['response']}")
    
    # Test Status Lookup Route
    sample_id = LOAN_APPLICATIONS[0]["record_id"]
    res2 = run_agent(f"Check status for application {sample_id}", thread_id="t1")
    print(f"\n[Turn 2 Intent: {res2['intent']}] -> Response:\n{res2['response']}")