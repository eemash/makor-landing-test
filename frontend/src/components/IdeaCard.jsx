import React, { useState } from "react";

function IdeaCard({ idea }) {
  const [expanded, setExpanded] = useState(true);
  const isCoffee = idea.category === "coffee";
  const categoryClass = isCoffee ? "coffee" : "general";
  const categoryLabel = isCoffee ? "Coffee" : "General CPG";

  const date = new Date(idea.created_at);
  const formattedDate = date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });

  return (
    <div className={`idea-card ${categoryClass}`}>
      <div className="card-header">
        <span className={`category-badge ${categoryClass}`}>
          {isCoffee ? "\u2615" : "\u2728"} {categoryLabel}
        </span>
      </div>

      <div className="brand-name">{idea.brand_name}</div>
      <div className="tagline">"{idea.tagline}"</div>

      <div className="meta-row">
        <div className="meta-item">
          <span className="meta-label">Product: </span>
          <span className="meta-value">{idea.product_type}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Target: </span>
          <span className="meta-value">{idea.target_audience}</span>
        </div>
      </div>

      <div
        style={{ cursor: "pointer", userSelect: "none" }}
        onClick={() => setExpanded(!expanded)}
      >
        <span style={{ color: "#71717a", fontSize: "0.85rem", fontWeight: 600 }}>
          {expanded ? "\u25BC" : "\u25B6"} Reasoning & Analysis
        </span>
      </div>

      {expanded && (
        <div className="reasoning" style={{ marginTop: "0.75rem" }}>
          {idea.reasoning}
        </div>
      )}

      {idea.trend_keywords && idea.trend_keywords.length > 0 && (
        <div className="trends-section">
          <div className="trends-title">Trend Keywords Analyzed</div>
          <div className="trend-tags">
            {idea.trend_keywords.map((kw, i) => (
              <span key={i} className="trend-tag">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="timestamp">{formattedDate}</div>
    </div>
  );
}

export default IdeaCard;
