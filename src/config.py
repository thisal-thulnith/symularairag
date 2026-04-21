from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
DATA_DIR = Path("./data")
VECTOR_DIR = Path("./vectorstore")
EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 5
