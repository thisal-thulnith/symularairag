from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from src import config
from src.retriever import get_retriever
from src.state import AgentState
from src.tools import create_calendly_link

llm = ChatOpenAI(model=config.LLM_MODEL, temperature=0)
retriever = get_retriever()


def route_intent(state: AgentState) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Classify the user's intent. Reply with EXACTLY one word:\n"
         "- 'booking' if they want to book a meeting, schedule a call, "
         "talk to someone, or request a demo\n"
         "- 'rag' for anything else (questions, info requests)"),
        ("user", "{q}"),
    ])
    out = (prompt | llm).invoke({"q": state["query"]})
    intent = out.content.strip().lower()
    return {"intent": "booking" if "booking" in intent else "rag"}


def book_meeting(state: AgentState) -> dict:
    link = create_calendly_link()
    if link.startswith("http"):
        answer = (
            f"Sure — here's your booking link: {link}\n\n"
            "It's a one-time link for a 30-minute meeting. "
            "Pick a slot that works for you."
        )
    else:
        answer = link
    return {
        "answer": answer,
        "messages": [HumanMessage(state["query"]), AIMessage(answer)],
    }


def rewrite_query(state: AgentState) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Rewrite the user query to be specific and search-friendly. "
         "Return only the rewritten query."),
        ("user", "{q}"),
    ])
    out = (prompt | llm).invoke({"q": state["query"]})
    return {"rewritten_query": out.content}


def retrieve(state: AgentState) -> dict:
    docs = retriever.invoke(state["rewritten_query"])
    return {"documents": docs, "attempts": state.get("attempts", 0) + 1}


def grade_documents(state: AgentState) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Are the documents relevant to the query? "
         "Answer only 'relevant' or 'irrelevant'."),
        ("user", "Query: {q}\n\nDocs:\n{d}"),
    ])
    joined = "\n---\n".join(d.page_content[:500] for d in state["documents"])
    out = (prompt | llm).invoke({"q": state["query"], "d": joined})
    return {"grade": out.content.strip().lower()}


def generate(state: AgentState) -> dict:
    context = "\n\n".join(d.page_content for d in state["documents"])
    history = state.get("messages", [])
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Answer using ONLY the context. If insufficient, say so. Cite sources."),
        ("placeholder", "{history}"),
        ("user", "Context:\n{c}\n\nQuestion: {q}"),
    ])
    out = (prompt | llm).invoke({
        "c": context, "q": state["query"], "history": history,
    })
    return {
        "answer": out.content,
        "messages": [HumanMessage(state["query"]), AIMessage(out.content)],
    }
