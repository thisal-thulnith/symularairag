import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from src.graph import build_graph

app = FastAPI(title="Symular RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()


class AskRequest(BaseModel):
    query: str
    thread_id: str = "default"


STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ask")
async def ask(req: AskRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    result = await graph.ainvoke(
        {"query": req.query, "attempts": 0},
        config=config,
    )
    return {"answer": result["answer"], "thread_id": req.thread_id}


@app.post("/ask/stream")
async def ask_stream(req: AskRequest):
    config = {"configurable": {"thread_id": req.thread_id}}

    async def event_generator():
        async for event in graph.astream_events(
            {"query": req.query, "attempts": 0},
            config=config,
            version="v2",
        ):
            kind = event["event"]

            if kind == "on_chain_start" and event["name"] in {
                "router", "book", "rewrite", "retrieve", "grade", "generate"
            }:
                yield {
                    "event": "node_start",
                    "data": json.dumps({"node": event["name"]}),
                }

            elif kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    yield {"event": "token", "data": chunk}

    return EventSourceResponse(event_generator())
