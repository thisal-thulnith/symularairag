from typing import TypedDict, Annotated
from langchain_core.documents import Document
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    query: str
    intent: str
    rewritten_query: str
    documents: list[Document]
    grade: str
    answer: str
    attempts: int
