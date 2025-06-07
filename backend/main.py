import uvicorn
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import json

app = FastAPI()
UPLOAD_DIR = "public/uploads"
META_FILE = "public/uploads/meta.json"

os.makedirs(UPLOAD_DIR, exist_ok=True)
if not os.path.exists(META_FILE):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="public"), name="static")
app.mount("/uploads", StaticFiles(directory="public/uploads"), name="uploads")

CATEGORIES = [
    "הפיקוח על הבנקים",
    "פיקוח על מערכות תשלומים",
    "מאגר נתוני אשראי",
]

def load_meta():
    with open(META_FILE, encoding="utf-8") as f:
        return json.load(f)

def save_meta(meta):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), category: str = Form(...)):
    if category not in CATEGORIES:
        return JSONResponse({"error": "קטגוריה לא קיימת"}, status_code=400)
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    meta = load_meta()
    meta.append({
        "filename": file.filename,
        "category": category
    })
    save_meta(meta)
    return {"success": True, "filename": file.filename, "category": category}

@app.get("/api/files")
def list_files():
    meta = load_meta()
    return meta

@app.post("/api/search")
async def search(query: dict):
    # בדמו: תוצאות מזויפות לפי השאלה
    q = query.get("query", "")
    # תוצאות דמה (להחליף באינדוקס אמיתי)
    results = {
        "הפיקוח על הבנקים": [],
        "פיקוח על מערכות תשלומים": [],
        "מאגר נתוני אשראי": [],
    }
    if "עמלות" in q or "בנק" in q:
        results["הפיקוח על הבנקים"].append("הוראת ניהול בנקאי תקין 301 מחייבת את הבנקים לפרסם מידע לציבור על עמלות עיקריות.")
        results["הפיקוח על הבנקים"].append("על פי חוזר 2021/12, יש לעדכן את הנהלים אחת לשנה.")
    if "תשלומים" in q or "אבטחת מידע" in q:
        results["פיקוח על מערכות תשלומים"].append("מערכת זה\"ב נדרשת לעמוד בתקני אבטחת מידע המפורטים בחוזר 511.")
    if "אשראי" in q:
        results["מאגר נתוני אשראי"].append("מאגר נתוני אשראי מרכז מידע אודות התנהלות כלכלית של לקוחות.")
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)