import { useEffect, useMemo, useState } from "react";
import TicketCard from "../components/TicketCard";
import { getBoard } from "../services/api";

export default function Dashboard({ onSimulate }) {
  const [board, setBoard] = useState({ auto_resolved: [], human_review: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    fetchBoard();
  }, []);

  const fetchBoard = () => {
    setLoading(true);
    getBoard()
      .then((data) => {
        setBoard(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  const handleApprove = (ticket) => {
    alert(`Approved: ${ticket.ticket_id} -> ${ticket.action}`);
  };

  const handleOverride = (ticket) => {
    alert(`Override requested for: ${ticket.ticket_id}`);
  };

  const filterFn = (t) => {
    if (!query.trim()) return true;
    const q = query.toLowerCase();
    return (
      t.ticket_id.toLowerCase().includes(q) ||
      t.order_id.toLowerCase().includes(q) ||
      t.description.toLowerCase().includes(q)
    );
  };

  const autoResolved = useMemo(() => board.auto_resolved.filter(filterFn), [board, query]);
  const humanReview = useMemo(() => board.human_review.filter(filterFn), [board, query]);
  const total = board.auto_resolved.length + board.human_review.length;

  if (loading) return <div className="status-message">Loading tickets...</div>;
  if (error) return <div className="status-message error">Error: {error}</div>;

  return (
    <div>
      <div className="stat-strip">
        <span className="stat online">
          <span className="dot" /> System Online
        </span>
        <span className="stat neutral">Tickets <b>{total}</b></span>
        <span className="stat auto">Auto-Resolved <b>{board.auto_resolved.length}</b></span>
        <span className="stat human">Needs Human <b>{board.human_review.length}</b></span>
        <button className="refresh-btn" onClick={fetchBoard}>⟳ Refresh</button>
      </div>

      <div className="toolbar">
        <input
          className="search-input"
          type="text"
          placeholder="Search ticket, order, or description..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="simulate-btn" onClick={onSimulate}>
          + Simulate New Ticket
        </button>
      </div>

      <div className="board">
        <div className="lane">
          <div className="lane-heading">
            <div>
              <h2 className="lane-title auto">✓ Auto-Resolved</h2>
              <span className="lane-sub">Safe to automate</span>
            </div>
            <span className="lane-count auto">{autoResolved.length} tickets</span>
          </div>
          <div className="lane-content">
            {autoResolved.map((ticket) => (
              <TicketCard key={ticket.ticket_id} ticket={ticket} onApprove={handleApprove} onOverride={handleOverride} />
            ))}
          </div>
        </div>

        <div className="lane">
          <div className="lane-heading">
            <div>
              <h2 className="lane-title human">⚠ Needs Human</h2>
              <span className="lane-sub">Human decision required</span>
            </div>
            <span className="lane-count human">{humanReview.length} tickets</span>
          </div>
          <div className="lane-content">
            {humanReview.map((ticket) => (
              <TicketCard key={ticket.ticket_id} ticket={ticket} onApprove={handleApprove} onOverride={handleOverride} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}