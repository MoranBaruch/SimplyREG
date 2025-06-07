import React from "react";

export default function AnswerBox({ answer, sources }) {
  if (!answer) return null;
  return (
    <div className="answer-box">
      <h3>תשובה:</h3>
      <div style={{ whiteSpace: "pre-line" }}>{answer}</div>
      {sources.length > 0 && (
        <div className="sources">
          <h4>קטעים רלוונטיים:</h4>
          <ul>
            {sources.map((src, i) => (
              <li key={i}>{src.filename ? src.filename : JSON.stringify(src)}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}