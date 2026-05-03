import { useState } from "react";

export default function App() {
  const [code, setCode] = useState("");
  const [explanation, setExplanation] = useState("");
  const [output, setOutput] = useState("");
  const [finalCode, setFinalCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const send = async () => {
    setLoading(true);
    setExplanation("");
    setOutput("");
    setFinalCode("");
    setError("");

    try {
      const res = await fetch("http://127.0.0.1:8000/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      });

      const data = await res.json();

      setExplanation(data.explanation || "");
      setOutput(data.output || "");
      setFinalCode(data.final_code || "");

      if (data.error) {
        setError(data.error);
      }
    } catch (err) {
      setError("Backend request failed ", err);
    }

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

          <pre style={styles.output}>
            {loading ? "Thinking..." : explanation || "No explanation yet"}
          </pre>

          {error && (
            <pre style={{ ...styles.output, color: "red" }}>{error}</pre>
          )}

          <h3 style={{ marginTop: 20 }}>Execution Output</h3>
          <pre style={styles.output}>
            {loading ? "Running..." : output || "No output yet"}
          </pre>

          <h3 style={{ marginTop: 20 }}>Final Code</h3>
          <pre style={styles.output}>
            {loading ? "Processing..." : finalCode || "No fixed code yet"}
          </pre>
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
