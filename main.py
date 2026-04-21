import asyncio
from src.graph import build_graph

graph = build_graph()


async def ask(query: str, thread_id: str = "default") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = await graph.ainvoke(
        {"query": query, "attempts": 0},
        config=config,
    )
    return result["answer"]


async def main():
    print(await ask("What is Symular AI?", thread_id="u1"))
    print("---")
    print(await ask("I'd like to book a demo", thread_id="u1"))


if __name__ == "__main__":
    asyncio.run(main())
