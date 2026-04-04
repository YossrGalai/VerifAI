import React, { useState } from "react";
import { uploadImage } from "./api";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    const data = await uploadImage(file);
    setResult(data);
  };

  const getConfidenceColor = (score) => {
    if (score > 0.8) return "green";
    if (score > 0.5) return "orange";
    return "red";
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>Vérification de contenu</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files[0])} />
        <button type="submit" style={{ marginLeft: "1rem" }}>Vérifier</button>
      </form>

      {result && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Texte OCR :</h2>
          <div style={{ padding: "1rem", background: "#f0f0f0", borderRadius: "5px" }}>
            {result.structured_data.original_text || "Aucun texte détecté"}
          </div>

          <h2 style={{ marginTop: "1.5rem" }}>Score de confiance :</h2>
          <div style={{
            width: "100%",
            height: "25px",
            background: "#ddd",
            borderRadius: "5px",
            overflow: "hidden"
          }}>
            <div style={{
              width: `${result.structured_data.confidence_score * 100}%`,
              height: "100%",
              background: getConfidenceColor(result.structured_data.confidence_score),
              textAlign: "center",
              color: "white",
              lineHeight: "25px",
              fontWeight: "bold"
            }}>
              {Math.round(result.structured_data.confidence_score * 100)}%
            </div>
          </div>

          <h2 style={{ marginTop: "1.5rem" }}>Sources fiables détectées :</h2>
          <ul>
            {result.structured_data.reverse_image_results.map((source, index) => (
              <li key={index}>
                <a href={source.url} target="_blank" rel="noopener noreferrer">{source.url}</a> - Similarité: {Math.round(source.similarity * 100)}%
              </li>
            ))}
          </ul>

          <h2 style={{ marginTop: "1.5rem" }}>Résumé LLM :</h2>
          <div style={{ padding: "1rem", background: "#e0f7fa", borderRadius: "5px" }}>
            {result.llm_analysis}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;