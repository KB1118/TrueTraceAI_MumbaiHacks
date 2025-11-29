interface Crisis {
  id: number;
  title: string;
  description: string;
  detected_at: string;
  status: string;
}

interface CrisisListProps {
  crises: Crisis[];
  selectedCrisis: number | null;
  onSelectCrisis: (id: number | null) => void;
  loading: boolean;
}

export default function CrisisList({ crises, selectedCrisis, onSelectCrisis, loading }: CrisisListProps) {
  if (loading) {
    return (
      <div className="crisis-list">
        <h3>Active Crises</h3>
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="crisis-list">
      <h3>Active Crises</h3>
      {crises.length === 0 ? (
        <div className="empty-state">No crises detected yet.</div>
      ) : (
        <div className="crisis-items">
          <button
            className={`crisis-item ${selectedCrisis === null ? 'active' : ''}`}
            onClick={() => onSelectCrisis(null)}
          >
            <span className="crisis-title">All Crises</span>
          </button>
          {crises.map((crisis) => (
            <button
              key={crisis.id}
              className={`crisis-item ${selectedCrisis === crisis.id ? 'active' : ''}`}
              onClick={() => onSelectCrisis(crisis.id)}
            >
              <span className="crisis-title">{crisis.title}</span>
              <span className="crisis-date">
                {new Date(crisis.detected_at).toLocaleDateString()}
              </span>
              <span className={`crisis-status status-${crisis.status}`}>
                {crisis.status}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

