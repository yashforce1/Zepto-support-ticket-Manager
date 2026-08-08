export default function PrecedentList({ precedents }) {
    if (!precedents || precedents.length === 0) return null;
  
    return (
      <div className="precedent-list">
        <h4>Top {precedents.length} Similar Historical Cases</h4>
        {precedents.map((p, i) => (
          <div key={p.ticket_id} className="precedent-card">
            <div className="precedent-header">
              <span className="precedent-rank">#{i + 1}</span>
              <span className="precedent-sim">{Math.round(p.similarity * 100)}% similarity</span>
            </div>
            <p className="precedent-desc">"{p.description}"</p>
            <div className="precedent-footer">
              <span className="precedent-action">{p.resolution_action}</span>
              <span className="precedent-note">{p.resolution_note}</span>
            </div>
          </div>
        ))}
      </div>
    );
  }