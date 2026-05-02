import { useState } from "react";

export default function App() {
  const [task, setTask] = useState("");
  const [response, setResponse] = useState("");

  const send = async () => {
    const res = await fetch("http://127.0.0.1:8000/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ task }),
    });

    const data = await res.json();
    console.log(data);
    setResponse(`CODE:\n${data.code}\n\nEXPLANATION:\n${data.explanation}`);
  };

  return (
    <div>
      <input value={task} onChange={(e) => setTask(e.target.value)} />
      <button onClick={send}>Send</button>
      <p>{response}</p>
    </div>
  );
}