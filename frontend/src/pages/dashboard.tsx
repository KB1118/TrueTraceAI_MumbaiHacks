import { useEffect, useState } from 'react';
import { crisisAPI, claimAPI, pipelineAPI } from '@/lib/api';
import Navbar from '@/components/Navbar';
import CrisisList from '@/components/CrisisList';
import RumorClusters from '@/components/RumorClusters';
import ClaimVerdictCard from '@/components/ClaimVerdictCard';

interface Crisis {
  id: number;
  title: string;
  description: string;
  detected_at: string;
  status: string;
}

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

export default function Dashboard() {
  const [crises, setCrises] = useState<Crisis[]>([]);
  const [selectedCrisis, setSelectedCrisis] = useState<number | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [verdictFilter, setVerdictFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [pipelineStatus, setPipelineStatus] = useState('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [selectedCrisis, verdictFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      setErrorMessage(null);
      const [crisesData, claimsData] = await Promise.all([
        crisisAPI.list(),
        claimAPI.list(selectedCrisis || undefined, verdictFilter !== 'all' ? verdictFilter : undefined)
      ]);
      setCrises(crisesData);
      setClaims(claimsData);
    } catch (error: any) {
      console.error('Failed to load data:', error);
      setErrorMessage(error.response?.data?.detail || 'Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerPipeline = async () => {
    try {
      await pipelineAPI.trigger();
      setPipelineStatus('running');
      setTimeout(() => {
        loadData();
        setPipelineStatus('idle');
      }, 5000);
    } catch (error) {
      console.error('Failed to trigger pipeline:', error);
    }
  };

  return (
    <div className="dashboard-page">
      <Navbar />
      
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>TrueTrace Radar Dashboard</h1>
          <button onClick={handleTriggerPipeline} className="btn btn-primary" disabled={pipelineStatus === 'running'}>
            {pipelineStatus === 'running' ? 'Processing...' : 'Trigger Pipeline'}
          </button>
        </div>

        <div className="dashboard-grid">
          <div className="dashboard-sidebar">
            <CrisisList
              crises={crises}
              selectedCrisis={selectedCrisis}
              onSelectCrisis={setSelectedCrisis}
              loading={loading}
            />
            
            <div className="filter-section">
              <h3>Filter by Verdict</h3>
              <select
                value={verdictFilter}
                onChange={(e) => setVerdictFilter(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Verdicts</option>
                <option value="True">True</option>
                <option value="False">False</option>
                <option value="Misleading">Misleading</option>
                <option value="Uncertain">Uncertain</option>
              </select>
            </div>
          </div>

          <div className="dashboard-main">
            {selectedCrisis && (
              <div className="clusters-section">
                <RumorClusters crisisId={selectedCrisis} />
              </div>
            )}

            <div className="claims-section">
              <h2>Verified Claims</h2>
              {errorMessage && <div className="error-message">{errorMessage}</div>}
              {loading ? (
                <div className="loading">Loading claims...</div>
              ) : claims.length === 0 ? (
                <div className="empty-state">No claims found. Trigger the pipeline to start processing.</div>
              ) : (
                <div className="claims-grid">
                  {claims.map((claim) => (
                    <ClaimVerdictCard key={claim.id} claim={claim} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

