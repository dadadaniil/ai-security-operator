from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_PORT=int(getenv("API_PORT"))
LLM_MODEL=getenv("LLM_MODEL")
VECTORSTORE_PATH=getenv("VECTORSTORE_PATH")
OLLAMA_URL=getenv("OLLAMA_URL")
