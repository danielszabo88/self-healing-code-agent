import { useState } from "react";

export default function App() {
  const [code, setCode] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    setLoading(true);
    setResponse("");

    const res = await fetch("http://127.0.0.1:8000/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ code }),
    });

    const data = await res.json();

    setResponse(data.explanation);
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>AI Code Explainer</h2>

      <div style={styles.grid}>
        {/* LEFT: INPUT */}
        <div style={styles.panel}>
          <h3>Input Code</h3>

          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here..."
            style={styles.textarea}
          />

          <button onClick={send} style={styles.button}>
            Explain
          </button>
        </div>

        {/* RIGHT: OUTPUT */}
        <div style={styles.panel}>
          <h3>Explanation</h3>

          {loading ? (
            <p>Thinking...</p>
          ) : (
            <pre style={styles.output}>
              {response || "Your explanation will appear here..."}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: 20,
    fontFamily: "Arial, sans-serif",
  },
  title: {
    marginBottom: 20,
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 20,
  },
  panel: {
    border: "1px solid #ddd",
    borderRadius: 8,
    padding: 15,
    background: "#fafafa",
  },
  textarea: {
    width: "100%",
    height: 250,
    padding: 10,
    fontFamily: "monospace",
    fontSize: 14,
  },
  button: {
    marginTop: 10,
    padding: "8px 12px",
    cursor: "pointer",
  },
  output: {
    whiteSpace: "pre-wrap",
    fontSize: 14,
    lineHeight: 1.5,
  },
};