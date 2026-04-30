import React, { useEffect, useState, useCallback } from "react";
import IdeaCard from "./components/IdeaCard";

function App() {
  const [todayIdeas, setTodayIdeas] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const fetchData = useCallback(() => {
    setLoading(true);
    return Promise.all([
      fetch("/api/ideas/today").then((r) => r.json()),
      fetch("/api/ideas/history").then((r) => r.json()),
    ])
      .then(([today, hist]) => {
        setTodayIdeas(today);
        setHistory(hist);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleGenerate = () => {
    setGenerating(true);
    fetch("/api/ideas/generate", { method: "POST" })
      .then((r) => r.json())
      .then(() => fetchData())
      .then(() => setGenerating(false))
      .catch(() => setGenerating(false));
  };

  return (
    <div className="app">
      <div className="header">
        <h1>CPG Idea Generator</h1>
        <p>
          Fresh brand ideas powered by Google Trends + AI — one coffee, one
          wildcard — delivered twice daily.
        </p>
        <button
          className="generate-btn"
          onClick={handleGenerate}
          disabled={generating}
        >
          {generating ? "Analyzing trends..." : "Generate New Ideas Now"}
        </button>
      </div>

      {generating && (
        <div className="loading">
          <div className="spinner" />
          <p className="generating-text">
            Fetching Google Trends data and generating ideas...
          </p>
          <p style={{ color: "#52525b", fontSize: "0.85rem" }}>
            This takes about 30 seconds
          </p>
        </div>
      )}

      {!loading && !generating && (
        <>
          <div className="section-title">Today's Ideas</div>
          {todayIdeas.length === 0 ? (
            <div className="empty-state">
              <p>No ideas generated today yet.</p>
              <p>Click the button above to generate your first pair!</p>
            </div>
          ) : (
            <div className="ideas-grid">
              {todayIdeas.map((idea) => (
                <IdeaCard key={idea.id} idea={idea} />
              ))}
            </div>
          )}

          {history.length > 0 && (
            <div className="history-section">
              <div className="section-title">Recent History</div>
              <div className="ideas-grid">
                {history
                  .filter(
                    (h) => !todayIdeas.some((t) => t.id === h.id),
                  )
                  .map((idea) => (
                    <IdeaCard key={idea.id} idea={idea} />
                  ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
