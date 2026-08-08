import { useState } from "react";

const ACTION_LABELS = {
  full_refund: "Full Refund",
  partial_refund: "Partial Refund",
  refund_reissue: "Refund Reissue",
  redelivery: "Redelivery",
  coupon: "Coupon",
  apology_no_action: "Apology (No Action)",
  escalation: "Escalation",
};

function confidenceColor(confidence) {
  if (confidence >= 0.7) return "var(--success)";
  if (confidence >= 0.4) return "var(--warning)";
  return "var(--danger)";
}

export default function TicketCard({ ticket, onApprove, onOverride }) {
  const [expanded, setExpanded] = useState(false);
  const isAuto = ticket.status === "auto_resolved";
  const pct = Math.round(ticket.confidence * 100);
  const actionLabel = ticket.action ? (ACTION_LABELS[ticket.action] || ticket.action) : "No action";

  return (
    <div className={`ticket-card ${isAuto ? "auto" : "human"}`}>
      <div className="ticket-header">
        <span className="ticket-id-badge">{ticket.ticket_id}</span>
        <span className="ticket-order">Order #{ticket.order_id}</span>
      </div>

      <p className="ticket-desc">{ticket.description}</p>

      <div className="ticket-row">
        <span className={`status-badge ${isAuto ? "auto" : "human"}`}>
          {isAuto ? "AUTO-RESOLVED" : "NEEDS HUMAN"}
        </span>
        <span className="suggested-action">
          {isAuto ? actionLabel : <>Suggested: <b>{actionLabel}</b></>}
        </span>
      </div>

      <div className="ticket-row confidence-row">
        <span className="confidence-label" style={{ color: confidenceColor(ticket.confidence) }}>
          {pct}% confidence
        </span>
        <span className={`delivery-label ${ticket.delivery_status}`}>
          {ticket.delivery_status}
        </span>
      </div>

      <div className="confidence-bar-bg">
        <div
          className="confidence-bar-fill"
          style={{ width: `${pct}%`, backgroundColor: confidenceColor(ticket.confidence) }}
        />
      </div>

      {!isAuto && (
        <p className="ticket-warning">⚠ {ticket.reason}</p>
      )}

      <button className="expand-btn" onClick={() => setExpanded(!expanded)}>
        {expanded ? "Hide" : "Show"} details ▾
      </button>

      {expanded && (
        <div className="ticket-details">
          {ticket.refund_amount && (
            <p className="detail-line"><b>Refund amount:</b> ₹{ticket.refund_amount}</p>
          )}
          <p className="detail-line"><b>Reason:</b> {ticket.reason}</p>

          <div className="ticket-reply">
            <strong>Drafted reply</strong>
            <p>{ticket.reply}</p>
          </div>

          <div className="precedents">
            <strong className="precedents-title">Top {ticket.precedents.length} precedents</strong>
            {ticket.precedents.map((p) => (
              <div key={p.ticket_id} className="precedent-item">
                <span className="precedent-id">{p.ticket_id}</span>
                <span className="precedent-action">{p.resolution_action}</span>
                <span className="precedent-sim">{Math.round(p.similarity * 100)}% match</span>
                <p className="precedent-desc">"{p.description}"</p>
              </div>
            ))}
          </div>

          {!isAuto && (
            <div className="human-controls">
              <button className="approve-btn" onClick={() => onApprove(ticket)}>
                ✓ Approve suggested action
              </button>
              <button className="override-btn" onClick={() => onOverride(ticket)}>
                Override
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}