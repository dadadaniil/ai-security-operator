from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_PORT=int(getenv("API_PORT"))
LLM_MODEL=getenv("LLM_MODEL")
VECTORSTORE_PATH=getenv("VECTORSTORE_PATH")
LLM_OUTPUT_TOKEN_LIMIT=int(getenv("LLM_OUTPUT_TOKEN_LIMIT"))  # Debug stuff to speed up gen
