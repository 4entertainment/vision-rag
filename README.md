## Backend: 
FastAPI, CLIP + bgem3 embeddings, 

## Frontend: 
HTML/CSS/JS + Tesseract.js,

## VideoCam: 
“Start Camera” gets 2frames every 2sec -> OCR -> RAG


## START:
-- Backend
```
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```