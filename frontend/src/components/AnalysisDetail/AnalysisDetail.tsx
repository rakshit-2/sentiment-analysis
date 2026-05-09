import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { analysisApi, transcriptApi } from '../../services/api';
import type { Analysis, Transcript } from '../../types/api.types';
import Loader from '../Loader';
import styles from './AnalysisDetail.module.scss';

const AnalysisDetail = () => {
  const { uuid } = useParams<{ uuid: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [transcript, setTranscript] = useState<Transcript | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (uuid) {
      loadAnalysisDetail(uuid);
    }
  }, [uuid]);

  const loadAnalysisDetail = async (analysisUuid: string) => {
    try {
      setLoading(true);
      setError(null);

      const analysisData = await analysisApi.getById(analysisUuid);
      setAnalysis(analysisData);

      // Fetch transcript if not included
      if (!analysisData.transcript && analysisData.transcript_id) {
        const transcriptData = await transcriptApi.getById(analysisData.transcript_id);
        setTranscript(transcriptData);
      } else if (analysisData.transcript) {
        setTranscript(analysisData.transcript);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analysis');
      console.error('Analysis detail error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    const from = (location.state as { from?: string })?.from;
    if (from) {
      navigate(from);
    } else {
      navigate('/dashboard');
    }
  };

  const getBackButtonText = () => {
    const from = (location.state as { from?: string })?.from;
    if (from === '/analysis') return '← Back to Analysis';
    if (from === '/dashboard') return '← Back to Dashboard';
    return '← Back';
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <Loader message="Loading analysis..." />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h3>Error loading analysis</h3>
          <p>{error || 'Analysis not found'}</p>
          <button onClick={handleBack} className={styles.backButton}>
            Back
          </button>
        </div>
      </div>
    );
  }

  const { result, status, created_at, analyzed_at, model_info } = analysis;

  return (
    <div className={styles.container}>
      <button onClick={handleBack} className={styles.backButton}>
        {getBackButtonText()}
      </button>

      <header className={styles.header}>
        <h1>{transcript?.metadata?.title || 'Analysis Details'}</h1>
        <div className={styles.headerMeta}>
          <span className={`${styles.status} ${styles[`status${status.charAt(0).toUpperCase() + status.slice(1)}`]}`}>
            {status}
          </span>
          <span className={styles.date}>
            Created: {new Date(created_at).toLocaleString()}
          </span>
          {analyzed_at && (
            <span className={styles.date}>
              Analyzed: {new Date(analyzed_at).toLocaleString()}
            </span>
          )}
        </div>
      </header>

      {result && (
        <>
          {/* Call Summary */}
          <section className={styles.section}>
            <h2>Call Summary</h2>
            <div className={styles.summaryGrid}>
              <div className={styles.summaryCard}>
                <div className={styles.summaryLabel}>Overall Sentiment</div>
                <div className={`${styles.summaryValue} ${styles[`sentiment${result.summary.overall_call_sentiment}`]}`}>
                  {result.summary.overall_call_sentiment}
                </div>
              </div>
              <div className={styles.summaryCard}>
                <div className={styles.summaryLabel}>Lead Temperature</div>
                <div className={styles.summaryValue}>{result.summary.lead_temperature}</div>
              </div>
              <div className={styles.summaryCard}>
                <div className={styles.summaryLabel}>Meeting Likelihood</div>
                <div className={styles.summaryValue}>{result.summary.meeting_likelihood}%</div>
              </div>
              <div className={styles.summaryCard}>
                <div className={styles.summaryLabel}>Follow-up Readiness</div>
                <div className={styles.summaryValue}>{result.summary.follow_up_readiness}%</div>
              </div>
            </div>
          </section>

          {/* Primary Metrics */}
          <section className={styles.section}>
            <h2>Primary Metrics</h2>
            <div className={styles.metricsGrid}>
              {Object.entries(result.primary_metrics).map(([key, metric]) => (
                <div key={key} className={styles.metricCard}>
                  <div className={styles.metricHeader}>
                    <h3>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
                    <div className={styles.score}>{metric.score}/10</div>
                  </div>
                  <p className={styles.rationale}>{metric.rationale}</p>
                  {metric.evidence.length > 0 && (
                    <div className={styles.evidence}>
                      <strong>Evidence:</strong>
                      <ul>
                        {metric.evidence.map((item: string, idx: number) => (
                          <li key={idx}>"{item}"</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Key Insights */}
          <section className={styles.section}>
            <h2>Key Insights</h2>
            <div className={styles.insightsGrid}>
              {result.notable_buying_signals.length > 0 && (
                <div className={styles.insightCard}>
                  <h3>🎯 Buying Signals</h3>
                  <ul>
                    {result.notable_buying_signals.map((signal, idx) => (
                      <li key={idx}>{signal}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.objections_detected.length > 0 && (
                <div className={styles.insightCard}>
                  <h3>⚠️ Objections Detected</h3>
                  <ul>
                    {result.objections_detected.map((objection, idx) => (
                      <li key={idx}>{objection}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.risks_detected.length > 0 && (
                <div className={styles.insightCard}>
                  <h3>🚨 Risks Detected</h3>
                  <ul>
                    {result.risks_detected.map((risk, idx) => (
                      <li key={idx}>{risk}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.next_best_action.length > 0 && (
                <div className={styles.insightCard}>
                  <h3>✅ Next Best Actions</h3>
                  <ul>
                    {result.next_best_action.map((action, idx) => (
                      <li key={idx}>{action}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </section>
        </>
      )}

      {/* Transcript */}
      {transcript && (
        <section className={styles.section}>
          <h2>Full Transcript</h2>
          <div className={styles.transcriptBox}>
            <pre className={styles.transcriptText}>{transcript.transcript}</pre>
          </div>
        </section>
      )}

      {/* Model Info */}
      {model_info && (
        <section className={styles.section}>
          <h2>Model Information</h2>
          <div className={styles.modelInfo}>
            <div><strong>Model:</strong> {model_info.model}</div>
            {model_info.tokens_used && <div><strong>Tokens Used:</strong> {model_info.tokens_used.toLocaleString()}</div>}
            {model_info.cost && <div><strong>Cost:</strong> ${model_info.cost.toFixed(4)}</div>}
          </div>
        </section>
      )}
    </div>
  );
};

export default AnalysisDetail;
