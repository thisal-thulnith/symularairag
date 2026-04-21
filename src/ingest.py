from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src import config


def load_documents() -> list[Document]:
    docs = []
    for pdf in config.DATA_DIR.rglob("*.pdf"):
        docs.extend(PyPDFLoader(str(pdf)).load())
    for md in config.DATA_DIR.rglob("*.md"):
        docs.append(Document(
            page_content=md.read_text(encoding="utf-8"),
            metadata={"source": str(md)},
        ))
    return docs


def build_index():
    docs = load_documents()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)

    Chroma.from_documents(
        chunks,
        embedding=OpenAIEmbeddings(model=config.EMBED_MODEL),
        persist_directory=str(config.VECTOR_DIR),
    )
    print(f"Indexed {len(chunks)} chunks from {len(docs)} docs")


if __name__ == "__main__":
    build_index()
