interface Claim {
  id: number;
  text: string;
  verdict: string;
  confidence_score: number;
  volatility_score: number;
  reasoning: string;
  evidence_citations: string[];
  created_at: string;
}

interface ClaimVerdictCardProps {
  claim: Claim;
}

export default function ClaimVerdictCard({ claim }: ClaimVerdictCardProps) {
  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'True':
        return 'verdict-true';
      case 'False':
        return 'verdict-false';
      case 'Misleading':
        return 'verdict-misleading';
      case 'Uncertain':
        return 'verdict-uncertain';
      default:
        return 'verdict-uncertain';
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'high';
    if (score >= 0.5) return 'medium';
    return 'low';
  };

  return (
    <div className={`claim-card ${getVerdictColor(claim.verdict)}`}>
      <div className="claim-header">
        <span className={`verdict-badge ${getVerdictColor(claim.verdict)}`}>
          {claim.verdict}
        </span>
        <span className="claim-date">
          {new Date(claim.created_at).toLocaleDateString()}
        </span>
      </div>
      
      <div className="claim-text">
        <p>{claim.text}</p>
      </div>
      
      <div className="claim-metrics">
        <div className="metric">
          <span className="metric-label">Confidence</span>
          <span className={`metric-value confidence-${getConfidenceColor(claim.confidence_score)}`}>
            {(claim.confidence_score * 100).toFixed(0)}%
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Volatility</span>
          <span className="metric-value">
            {(claim.volatility_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>
      
      {claim.reasoning && (
        <div className="claim-reasoning">
          <h4>Reasoning</h4>
          <p>{claim.reasoning}</p>
        </div>
      )}
      
      {claim.evidence_citations && claim.evidence_citations.length > 0 && (
        <div className="claim-evidence">
          <h4>Evidence Sources</h4>
          <ul>
            {claim.evidence_citations.map((url, index) => (
              <li key={index}>
                <a href={url} target="_blank" rel="noopener noreferrer">
                  {url}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

