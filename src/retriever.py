from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from src import config


def get_retriever():
    vs = Chroma(
        persist_directory=str(config.VECTOR_DIR),
        embedding_function=OpenAIEmbeddings(model=config.EMBED_MODEL),
    )
    return vs.as_retriever(search_kwargs={"k": config.TOP_K})
