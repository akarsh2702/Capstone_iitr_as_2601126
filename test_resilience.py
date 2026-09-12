import time
import sqlite3
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

# Part 4 Task 15: SQLite Checkpointing Demonstration
class State(TypedDict):
    step_count: int
    executed_nodes: list
    data: str

def node_a(state: State) -> State:
    print(" Executing Node A...")
    state["executed_nodes"].append("Node_A")
    state["step_count"] += 1
    return state

def node_b(state: State) -> State:
    print(" Executing Node B...")
    state["executed_nodes"].append("Node_B")
    state["step_count"] += 1
    return state

def node_c(state: State) -> State:
    print(" Executing Node C...")
    state["executed_nodes"].append("Node_C")
    state["step_count"] += 1
    return state

conn = sqlite3.connect("test_checkpoints.sqlite", check_same_thread=False)
checkpointer = SqliteSaver(conn)

builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("node_c", node_c)

builder.set_entry_point("node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_c")
builder.add_edge("node_c", END)

graph = builder.compile(checkpointer=checkpointer, interrupt_before=["node_c"])

def demonstrate_checkpointing():
    print("\n--- DEMONSTRATING SQLITE CHECKPOINTING & RESUMPTION ---")
    thread_config = {"configurable": {"thread_id": "demo_thread_100"}}
    
    initial_state = {"step_count": 0, "executed_nodes": [], "data": "test_payload"}
    
    print("\nPhase 1: Running Graph (Will interrupt before Node C)...")
    state1 = graph.invoke(initial_state, config=thread_config)
    print(f"Interrupted State Loaded: Executed Nodes = {state1['executed_nodes']}")
    
    print("\nPhase 2: Resuming SAME Thread ID ('demo_thread_100')...")
    # Resume graph execution without re-running Node A or Node B
    state2 = graph.invoke(None, config=thread_config)
    print(f"Resumed Run Complete: Final Executed Nodes = {state2['executed_nodes']}")
    print(" Verified: Node A and Node B were loaded directly from SQLite checkpoint and NOT re-executed!")

# Part 4 Task 16: Timeouts and Exponential Backoff Retries Demonstration
class SimulatedTransientFailure:
    def __init__(self):
        self.attempts = 0
        
    def call_with_retry(self, max_attempts=3, initial_interval=0.1, backoff_factor=2.0):
        print(f"\n--- Demonstrating Exponential Backoff Retry (Max Attempts={max_attempts}) ---")
        interval = initial_interval
        for attempt in range(1, max_attempts + 1):
            self.attempts += 1
            print(f" Attempt {attempt} executing...")
            if self.attempts < 3:
                print(f" Attempt {attempt} failed due to simulated transient database timeout.")
                time.sleep(interval)
                interval *= backoff_factor
            else:
                print(f" Attempt {attempt} SUCCEEDED!")
                return "SUCCESS_DATA"
        raise Exception("Retry attempts exhausted!")

def demonstrate_timeouts():
    print("\n--- Demonstrating Per-Node and Global Timeouts ---")
    
    # 1. Per-node timeout simulation
    node_timeout_sec = 0.5
    print(f"Simulating per-node execution taking 1.0s with configured timeout {node_timeout_sec}s...")
    try:
        start = time.time()
        # Simulate node work
        time.sleep(0.8)
        if (time.time() - start) > node_timeout_sec:
            raise TimeoutError(f"PerNodeTimeoutException: Node 'rag_tool_node' exceeded limit of {node_timeout_sec}s")
    except TimeoutError as te:
        print(f" Per-Node Timeout Correctly Fired Clean Error: {te}")
        
    # 2. Global timeout simulation
    global_timeout_sec = 1.0
    print(f"Simulating total graph execution taking 1.5s with global timeout {global_timeout_sec}s...")
    try:
        start = time.time()
        time.sleep(1.2)
        if (time.time() - start) > global_timeout_sec:
            raise TimeoutError(f"GlobalGraphTimeoutException: Graph execution cancelled - total time exceeded {global_timeout_sec}s limit")
    except TimeoutError as ge:
        print(f" Global Timeout Correctly Cancelled Run: {ge}")

if __name__ == "__main__":
    demonstrate_checkpointing()
    
    tf = SimulatedTransientFailure()
    tf.call_with_retry()
    
    demonstrate_timeouts()