from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import AgentState
from src.nodes import (
    route_intent,
    book_meeting,
    rewrite_query,
    retrieve,
    grade_documents,
    generate,
)

MAX_ATTEMPTS = 2


def after_router(state: AgentState) -> str:
    return "book" if state["intent"] == "booking" else "rewrite"


def after_grade(state: AgentState) -> str:
    if state["grade"] == "relevant" or state["attempts"] >= MAX_ATTEMPTS:
        return "generate"
    return "rewrite"


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("router", route_intent)
    g.add_node("book", book_meeting)
    g.add_node("rewrite", rewrite_query)
    g.add_node("retrieve", retrieve)
    g.add_node("grade", grade_documents)
    g.add_node("generate", generate)

    g.set_entry_point("router")
    g.add_conditional_edges("router", after_router, {
        "book": "book",
        "rewrite": "rewrite",
    })
    g.add_edge("book", END)

    g.add_edge("rewrite", "retrieve")
    g.add_edge("retrieve", "grade")
    g.add_conditional_edges("grade", after_grade, {
        "rewrite": "rewrite",
        "generate": "generate",
    })
    g.add_edge("generate", END)

    return g.compile(checkpointer=MemorySaver())
