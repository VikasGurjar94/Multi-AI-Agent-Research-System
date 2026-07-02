// src/App.jsx
import { useState } from "react";
import "./App.css";

function App() {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch("http://localhost:5000/api/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });
      const data = await res.json();
      setResult(data);
    } catch {
      setError("Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>AI research assistant</h1>
        <p>Multi-agent research, powered by LangChain</p>
      </header>

      <form onSubmit={handleSubmit} className="search-form">
        <input
          type="text"
          placeholder="Enter a research topic..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Researching..." : "Research"}
        </button>
      </form>

      {loading && (
        <p className="hint">
          This can take 30–60s — search, scrape, write, and critique all run in
          sequence.
        </p>
      )}
      {error && <p className="error">{error}</p>}

      {result && (
        <div className="results">
          <section>
            <h2>Final report</h2>
            <p className="report-text">{result.report}</p>
          </section>
          <section>
            <h2>Critic feedback</h2>
            <p className="report-text">{result.feedback}</p>
          </section>
          <details>
            <summary>Raw search results</summary>
            <p>{result.search_results}</p>
          </details>
          <details>
            <summary>Scraped content</summary>
            <p>{result.scraped_content}</p>
          </details>
        </div>
      )}
    </div>
  );
}

export default App;
