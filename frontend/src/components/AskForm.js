import React, { useState } from "react";
import axios from "axios";

export default function AskForm({ setAnswer, setSources }) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    setAnswer(""); setSources([]);
    setLoading(true);
    try {
      const res = await axios.post("/api/ask", { question });
      setAnswer(res.data.answer);
      setSources(res.data.sources || []);
    } catch (err) {
      setAnswer("שגיאה: " + (err.response?.data?.error || err.message));
      setSources([]);
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="ask-form">
      <label>
        שאל/י שאלה:
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="לדוג' מה הדרישות החוקיות לפרסום עמלות?"
        />
      </label>
      <button type="submit" disabled={!question.trim() || loading}>
        {loading ? "מחפש..." : "שאל"}
      </button>
    </form>
  );
}