# SimplyREG – חיפוש חכם במסמכים (RAG)

## דרישות
- Python 3.9+
- Node.js 18+
- מפתח OpenAI (ל־embeddings ול־GPT)

## התקנה והרצה

### צד שרת:
```bash
cd backend
pip install -r requirements.txt
export OPENAI_API_KEY=your-key-here
uvicorn main:app --reload
```

### צד לקוח:
```bash
cd frontend
npm install
npm start
```

## תיאור
מערכת להעלאת מסמכים, שאילת שאלות חכמות (בעברית) על המסמכים, קבלת תשובה מגובשת עם מקורות רלוונטיים. מבוסס RAG (חיפוש סמנטי + GPT).

---