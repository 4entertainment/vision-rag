from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from embeddings import EmbeddingIndexer, generate_response
import numpy as np
from PIL import Image
import io
import easyocr

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components once

app.mount("/", StaticFiles(directory="../frontend/public", html=True), name="frontend")
indexer = EmbeddingIndexer(model_name="BAAI/bge-m3", cuda_device="0")
reader = easyocr.Reader(['en','tr'], gpu=False)

class Query(BaseModel):
    text: str

@app.post("/upload_doc")
async def upload_doc(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode('utf-8')
    indexer.index_text(text)
    return {"status": "indexed"}

@app.post("/query")
async def rag_query(q: Query):
    results = indexer.search(q.text, limit=3)
    context = "\n---\n".join([r[1] for r in results])
    response = generate_response(context, q.text)
    return {"response": response}

# ─────────────────────────────────────────────
# Yeni eklenen OCR endpoint’i
@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    data = await file.read()
    image = Image.open(io.BytesIO(data)).convert('RGB')
    np_img = np.array(image)
    texts = reader.readtext(np_img, detail=0)
    combined = ' '.join(texts).strip()
    return {"text": combined}
# ─────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
