import React, { useState, useEffect } from "react";
import FileUpload from "./components/FileUpload";
import AskForm from "./components/AskForm";
import AnswerBox from "./components/AnswerBox";
import "./App.css";
import logo from "./logo.png";

export default function App() {
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [files, setFiles] = useState([]);

  const fetchFiles = async () => {
    try {
      const res = await fetch("/api/files");
      const arr = await res.json();
      setFiles(arr);
    } catch {}
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  return (
    <div className="App">
      <header>
        <img src={logo} alt="SimplyREG logo" className="logo" />
        <h1>SimplyREG - חיפוש חכם במסמכים</h1>
      </header>
      <main>
        <section>
          <FileUpload afterUpload={fetchFiles} />
          <div className="file-list-title">קבצים שהועלו:</div>
          <ul className="file-list">
            {files.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        </section>
        <section>
          <AskForm setAnswer={setAnswer} setSources={setSources} />
        </section>
        <section>
          <AnswerBox answer={answer} sources={sources} />
        </section>
      </main>
      <footer>
        <small>Powered by RAG & GPT • {new Date().getFullYear()}</small>
      </footer>
    </div>
  );
}