import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post("http://127.0.0.1:8000/analyze", formData);
    setResult(res.data);
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>VerifAI</h1>

      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Analyze</button>

      {result && (
        <div>
          <h2>Result:</h2>
          <p>Verdict: {result.verdict}</p>
          <p>Confidence: {result.confidence}%</p>
          <p>{result.explanation}</p>
        </div>
      )}
    </div>
  );
}

export default App;