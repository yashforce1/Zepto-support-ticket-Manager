const ACTION_LABELS = {
  full_refund: "Full Refund",
  partial_refund: "Partial Refund",
  refund_reissue: "Refund Reissue",
  redelivery: "Redelivery",
  coupon: "Coupon",
  apology_no_action: "Apology (No Action)",
  escalation: "Escalation",
};

export default function DecisionCard({ result }) {
  const isAuto = result.status === "auto_resolved";
  const pct = Math.round(result.confidence * 100);

  return (
    <div className={`decision-card ${isAuto ? "auto" : "human"}`}>
      <div className="decision-status">
        {isAuto ? "✅ AUTO-RESOLVE" : "⚠️ HUMAN REVIEW REQUIRED"}
      </div>

      <div className="decision-action">
        {result.action
          ? ACTION_LABELS[result.action] || result.action
          : "No action determined"}
        {result.refund_amount ? ` — ₹${result.refund_amount}` : ""}
      </div>

      <div className="decision-confidence">
        <div className="confidence-bar-bg">
          <div
            className="confidence-bar-fill"
            style={{
              width: `${pct}%`,
              backgroundColor:
                pct >= 70 ? "#27ae60" : pct >= 40 ? "#f39c12" : "#e74c3c",
            }}
          />
        </div>
        <span>{pct}% match confidence</span>
      </div>

      {!isAuto && pct >= 70 && (
        <p className="guardrail-note">
          ⚠ High similarity, but a policy guardrail overrode auto-resolution.
        </p>
      )}

      <div className="decision-reason">
        <strong>Why this decision?</strong>
        <p>{result.reason}</p>
      </div>

      {!isAuto && (
        <p className="human-note">
          The system has NOT automatically processed this ticket.
        </p>
      )}
    </div>
  );
}
