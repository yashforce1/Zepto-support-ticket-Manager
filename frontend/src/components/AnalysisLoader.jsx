import { useEffect, useState } from "react";

const STEPS = [
  "Reading ticket",
  "Fetching order context",
  "Searching historical tickets",
  "Finding top precedents",
  "Checking action consistency",
  "Applying business rules",
  "Calculating confidence",
];

export default function AnalysisLoader() {
  const [visibleCount, setVisibleCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setVisibleCount((c) => (c < STEPS.length ? c + 1 : c));
    }, 180);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="analysis-loader">
      <h3>Analyzing ticket...</h3>
      <ul>
        {STEPS.map((step, i) => (
          <li key={i} className={i < visibleCount ? "done" : "pending"}>
            {i < visibleCount ? "✓" : "○"} {step}
          </li>
        ))}
      </ul>
    </div>
  );
}