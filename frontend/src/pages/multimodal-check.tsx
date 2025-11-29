import { ChangeEvent, FormEvent, useMemo, useState } from 'react';
import Navbar from '@/components/Navbar';
import { factCheckAPI } from '@/lib/api';

interface SourceReference {
  id?: string | null;
  title?: string | null;
  snippet?: string | null;
  uri?: string | null;
}

interface SourceMetadata {
  rendered_content?: string | null;
  references?: SourceReference[] | null;
}

interface FileMetadata {
  name?: string | null;
  display_name?: string | null;
  mime_type?: string | null;
  state?: string | null;
  size_bytes?: number | null;
}

interface FactCheckResult {
  model: string;
  analysis_text: string;
  verdict_summary?: string | null;
  sources?: SourceMetadata | null;
  file?: FileMetadata | null;
  latency_ms?: number | null;
  used_google_search: boolean;
}

export default function MultimodalCheckPage() {
  const [textInput, setTextInput] = useState('');
  const [contextInput, setContextInput] = useState('Forwarded many times on WhatsApp');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FactCheckResult | null>(null);

  const fileLabel = useMemo(() => {
    if (!file) return 'Attach video, audio, or image evidence';
    const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
    return `${file.name} • ${sizeMb} MB`;
  }, [file]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0];
    setFile(selected ?? null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setResult(null);

    if (!file && !textInput.trim()) {
      setError('Please upload a file or supply a text description to analyze.');
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      }
      if (textInput.trim()) {
        formData.append('text', textInput.trim());
      }
      if (contextInput.trim()) {
        formData.append('context', contextInput.trim());
      }

      const response = await factCheckAPI.analyze(formData);
      setResult(response);
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        'Failed to analyze the supplied evidence.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fact-check-page">
      <Navbar />

      <main className="fact-check-container">
        <section className="fact-check-card glass">
          <div className="fact-check-header">
            <div>
              <p className="fact-check-pill">New</p>
              <h1>Multimodal Fact Checker</h1>
              <p className="fact-check-subtitle">
                Upload audio, video, or imagery plus optional text context. Gemini 2.5 Flash will
                transcribe, extract factual claims, verify them with grounded Google Search, and
                return a verdict you can trust.
              </p>
            </div>
          </div>

          <form className="fact-check-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="evidenceFile">Evidence Upload</label>
              <label className="file-drop">
                <input
                  id="evidenceFile"
                  type="file"
                  accept="image/*,video/*,audio/*"
                  onChange={handleFileChange}
                />
                <span>{fileLabel}</span>
                <small>Supported: images, video, and audio clips under 25 MB.</small>
              </label>
            </div>

            <div className="form-group">
              <label htmlFor="textInput">Describe the claim (optional)</label>
              <textarea
                id="textInput"
                placeholder="Paste the caption, WhatsApp forward, or textual rumor here..."
                value={textInput}
                onChange={(event) => setTextInput(event.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="contextInput">Context / Provenance</label>
              <input
                id="contextInput"
                type="text"
                value={contextInput}
                onChange={(event) => setContextInput(event.target.value)}
                placeholder="Ex: Forwarded in a community Telegram channel"
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? 'Analyzing evidence...' : 'Verify content'}
            </button>
            <p className="fact-check-hint">
              We never store raw uploads. Files are streamed to Gemini 2.5 for on-the-fly analysis,
              then deleted.
            </p>
          </form>
        </section>

        {result && (
          <section className="fact-check-result glass">
            <div className="result-header">
              <div>
                <p className="result-label">Analysis Complete</p>
                {result.verdict_summary && <h2>{result.verdict_summary}</h2>}
                <p className="result-model">
                  Model: {result.model} •{' '}
                  {result.latency_ms ? `${(result.latency_ms / 1000).toFixed(1)}s latency` : 'LLM'}
                </p>
              </div>
              {result.used_google_search && <span className="search-pill">Google Search Grounded</span>}
            </div>

            <div className="result-body">
              <h3>Investigator Notes</h3>
              <p className="analysis-text">{result.analysis_text}</p>
            </div>

            {result.sources && (
              <div className="result-sources">
                <h3>Source Trail</h3>
                {result.sources.rendered_content && (
                  <div
                    className="rendered-sources"
                    dangerouslySetInnerHTML={{ __html: result.sources.rendered_content }}
                  />
                )}
                {result.sources.references && (
                  <ul>
                    {result.sources.references.map((reference, index) => (
                      <li key={reference.id || index}>
                        <p className="reference-title">{reference.title || 'Referenced Source'}</p>
                        {reference.snippet && <p className="reference-snippet">{reference.snippet}</p>}
                        {reference.uri && (
                          <a href={reference.uri} target="_blank" rel="noreferrer">
                            {reference.uri}
                          </a>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {result.file && (
              <div className="result-file">
                <h3>Processed File</h3>
                <div className="file-meta-grid">
                  <div>
                    <p className="meta-label">Name</p>
                    <p className="meta-value">{result.file.display_name || result.file.name || '—'}</p>
                  </div>
                  <div>
                    <p className="meta-label">Type</p>
                    <p className="meta-value">{result.file.mime_type || 'Auto-detected'}</p>
                  </div>
                  <div>
                    <p className="meta-label">Size</p>
                    <p className="meta-value">
                      {result.file.size_bytes ? `${(result.file.size_bytes / (1024 * 1024)).toFixed(2)} MB` : '—'}
                    </p>
                  </div>
                  <div>
                    <p className="meta-label">State</p>
                    <p className="meta-value">{result.file.state || 'READY'}</p>
                  </div>
                </div>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

