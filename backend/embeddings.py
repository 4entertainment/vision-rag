import os
import subprocess
from txtai import Embeddings

class EmbeddingIndexer:
    def __init__(self, model_name="BAAI/bge-m3", cuda_device="0"):
        os.environ["CUDA_VISIBLE_DEVICES"] = cuda_device
        self.embeddings = Embeddings(path=model_name, hybrid=True, content=True, method="clspooling")

    def index_text(self, text: str):
        self.embeddings.index([(None, text, {})])

    def search(self, query: str, limit: int = 3):
        return self.embeddings.search(query, limit)


def generate_response(context: str, query_text: str) -> str:
    prompt = f"""
Sistem Talimatları:
Sen yalnızca Türkçe yanıt veren bir yapay zeka asistanısın.
Başka bir dilde yanıt vermemelisin.

--- BAĞLAM ---
{context}

--- SORU ---
{query_text}

--- YANIT ---
"""
    try:
        result = subprocess.run([
            "ollama", "run", "gemma3:12b", prompt
        ], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Ollama hatası: {e.stderr.strip()}"
