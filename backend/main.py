import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from PyPDF2 import PdfReader
import docx
import chromadb
import openai

# הגדרת מפתח OpenAI דרך משתנה סביבה
openai.api_key = os.getenv("OPENAI_API_KEY")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ChromaDB לאחסון embeddings
chroma_client = chromadb.Client()
collection = chroma_client.create_collection("docs")

def extract_text_pdf(path):
    text = ""
    reader = PdfReader(path)
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text

def extract_text_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text(path):
    if path.endswith(".pdf"):
        return extract_text_pdf(path)
    elif path.endswith(".docx"):
        return extract_text_docx(path)
    elif path.endswith(".txt"):
        with open(path, encoding="utf-8") as f:
            return f.read()
    else:
        return ""

def chunk_text(text, max_len=512):
    lines = text.split('\n')
    chunks, chunk = [], ""
    for line in lines:
        if len(chunk) + len(line) < max_len:
            chunk += line + "\n"
        else:
            if chunk.strip():
                chunks.append(chunk.strip())
            chunk = line + "\n"
    if chunk.strip():
        chunks.append(chunk.strip())
    return chunks

def get_embeddings(texts):
    response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
    return [d["embedding"] for d in response["data"]]

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt"]:
        return JSONResponse({"error": "נתמך רק PDF, DOCX, TXT"}, status_code=400)
    save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    text = extract_text(save_path)
    if not text.strip():
        return JSONResponse({"error": "לא נמצא טקסט בקובץ"}, status_code=400)
    chunks = chunk_text(text)
    embeddings = get_embeddings(chunks)
    ids = [str(uuid.uuid4()) for _ in chunks]
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=ids,
        metadatas=[{"filename": file.filename}] * len(chunks)
    )
    return {"success": True, "chunks": len(chunks), "filename": file.filename}

@app.get("/api/files")
def list_files():
    files = os.listdir(UPLOAD_DIR)
    return files

@app.post("/api/ask")
async def ask(data: dict):
    question = data.get("question", "")
    if not question:
        return JSONResponse({"error": "לא הוזנה שאלה"}, status_code=400)
    q_emb = get_embeddings([question])[0]
    results = collection.query(query_embeddings=[q_emb], n_results=5)
    docs = results["documents"][0]
    metadatas = results["metadatas"][0]
    prompt = (
        "ענה בעברית, על השאלה, על בסיס המידע הבא (ייתכן שמגיע ממסמכים שונים):\n"
        + "\n---\n".join(docs)
        + f"\n\nשאלה: {question}\nתשובה:"
    )
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.2,
    )
    answer = completion["choices"][0]["message"]["content"]
    return {"answer": answer, "sources": metadatas}
