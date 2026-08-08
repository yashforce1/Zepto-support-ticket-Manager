import { useState } from "react";
import { analyzeTicket } from "../services/api";
import AnalysisLoader from "../components/AnalysisLoader";
import DecisionCard from "../components/DecisionCard";
import PrecedentList from "../components/PrecedentList";
import OrderContext from "../components/OrderContext";
import CustomerReply from "../components/CustomerReply";

const EXAMPLES = [
  { label: "Missing item (clear case)", description: "milk packet missing from my order", order_id: "ORD-9900" },
  { label: "Cancelled order + redelivery (blocked)", description: "milk packet missing from my order", order_id: "ORD-9900" },
  { label: "Novel/unclear ticket", description: "the app crashed while I was checking my order status and now I'm confused about everything", order_id: "" },
];

export default function Analyze() {
  const [description, setDescription] = useState("");
  const [orderId, setOrderId] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!description.trim()) return;
    setAnalyzing(true);
    setResult(null);
    setError(null);

    try {
      // Small artificial delay so the loader is visible (better demo feel)
      const [data] = await Promise.all([
        analyzeTicket(description, orderId),
        new Promise((r) => setTimeout(r, 1400)),
      ]);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const loadExample = (ex) => {
    setDescription(ex.description);
    setOrderId(ex.order_id);
    setResult(null);
    setError(null);
  };

  return (
    <div className="analyze-page">
      <div className="input-panel">
        <h2>Paste a customer support ticket</h2>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="e.g. My milk packet was missing from my order."
          rows={4}
        />
        <input
          type="text"
          value={orderId}
          onChange={(e) => setOrderId(e.target.value)}
          placeholder="Order ID (optional) e.g. ORD-9900"
        />
        <button
          className="analyze-btn"
          onClick={handleAnalyze}
          disabled={analyzing || !description.trim()}
        >
          {analyzing ? "Analyzing..." : "Analyze Ticket"}
        </button>

        <div className="examples">
          <span>Try an example:</span>
          {EXAMPLES.map((ex, i) => (
            <button key={i} className="example-btn" onClick={() => loadExample(ex)}>
              {ex.label}
            </button>
          ))}
        </div>
      </div>

      {analyzing && <AnalysisLoader />}

      {error && <div className="error-box">Error: {error}</div>}

      {result && !analyzing && (
        <div className="result-panel">
          <DecisionCard result={result} />
          <OrderContext order={result.order} />
          <PrecedentList precedents={result.precedents} />
          <CustomerReply reply={result.reply} />
        </div>
      )}
    </div>
  );
}