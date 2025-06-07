import React, { useState } from "react";
import axios from "axios";

export default function FileUpload({ afterUpload }) {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");

  const handleChange = (e) => {
    setFile(e.target.files[0]);
    setMsg("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setMsg("מעלה קובץ...");
    const data = new FormData();
    data.append("file", file);
    try {
      const res = await axios.post("/api/upload", data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMsg(`הקובץ "${res.data.filename}" הועלה (${res.data.chunks} קטעים)`);
      setFile(null);
      afterUpload && afterUpload();
    } catch (err) {
      setMsg("שגיאת העלאה: " + (err.response?.data?.error || err.message));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <label>
        בחרי קובץ (PDF, DOCX, TXT):
        <input type="file" onChange={handleChange} accept=".pdf,.docx,.txt" />
      </label>
      <button type="submit" disabled={!file}>העלה</button>
      <div className="msg">{msg}</div>
    </form>
  );
}