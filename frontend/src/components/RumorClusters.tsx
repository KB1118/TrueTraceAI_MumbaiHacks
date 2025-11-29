import { useEffect, useState } from 'react';
import { clusterAPI } from '@/lib/api';

interface Cluster {
  id: number;
  topic_label: string;
  created_at: string;
  post_ids: string[];
}

interface RumorClustersProps {
  crisisId: number;
}

export default function RumorClusters({ crisisId }: RumorClustersProps) {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadClusters();
  }, [crisisId]);

  const loadClusters = async () => {
    try {
      setLoading(true);
      const data = await clusterAPI.listByCrisis(crisisId);
      setClusters(data);
    } catch (error) {
      console.error('Failed to load clusters:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="rumor-clusters">
        <h3>Rumor Clusters</h3>
        <div className="loading">Loading clusters...</div>
      </div>
    );
  }

  return (
    <div className="rumor-clusters">
      <h3>Rumor Clusters</h3>
      {clusters.length === 0 ? (
        <div className="empty-state">No clusters found for this crisis.</div>
      ) : (
        <div className="clusters-grid">
          {clusters.map((cluster) => (
            <div key={cluster.id} className="cluster-card">
              <h4>{cluster.topic_label || 'Unnamed Cluster'}</h4>
              <p className="cluster-meta">
                {cluster.post_ids?.length || 0} posts • {new Date(cluster.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

