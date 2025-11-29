import { useRouter } from 'next/router';
import Link from 'next/link';
import Navbar from '@/components/Navbar';

export default function Home() {
  const router = useRouter();

  return (
    <div className="home-page">
      <Navbar />
      
      <main className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">TrueTrace AI</h1>
          <p className="hero-subtitle">Agentic Misinformation Detection and Verification</p>
          <p className="hero-description">
            TrueTrace Radar automatically monitors global information streams, detects emerging misinformation,
            and provides transparent, evidence-based fact-checking powered by advanced AI reasoning.
          </p>
          
          <div className="hero-features">
            <div className="feature-card">
              <h3>Real-Time Monitoring</h3>
              <p>Continuously scans trusted news sources and social platforms for emerging crises and rumors</p>
            </div>
            <div className="feature-card">
              <h3>Intelligent Clustering</h3>
              <p>Uses semantic analysis and topic modeling to identify rumor clusters and extract canonical claims</p>
            </div>
            <div className="feature-card">
              <h3>Evidence-Based Verification</h3>
              <p>Retrieves evidence from authoritative sources and applies NLI + LLM reasoning for accurate verdicts</p>
            </div>
            <div className="feature-card">
              <h3>Transparent Results</h3>
              <p>Provides confidence scores, volatility metrics, and detailed reasoning paths for every claim</p>
            </div>
          </div>
          
          <div className="hero-cta">
            <Link href="/dashboard" className="btn btn-primary">
              View Dashboard
            </Link>
            <Link href="/login" className="btn btn-secondary">
              Login
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}

