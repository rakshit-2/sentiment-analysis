import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { transcriptApi, analysisApi } from '../../services/api';
import type { Transcript, Analysis } from '../../types/api.types';
import { formatISTFull, formatISTDate } from '../../utils/dateUtils';
import Loader from '../Loader';
import styles from './TranscriptDetail.module.scss';

const TranscriptDetail = () => {
  const { uuid } = useParams<{ uuid: string }>();
  const navigate = useNavigate();
  const [transcript, setTranscript] = useState<Transcript | null>(null);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (uuid) {
      loadTranscriptDetail(uuid);
    }
  }, [uuid]);

  const loadTranscriptDetail = async (transcriptUuid: string) => {
    try {
      setLoading(true);
      setError(null);

      // Fetch transcript and its analyses in parallel
      const [transcriptData, analysesData] = await Promise.all([
        transcriptApi.getById(transcriptUuid),
        analysisApi.getByTranscript(transcriptUuid),
      ]);

      setTranscript(transcriptData);
      setAnalyses(analysesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load transcript');
      console.error('Transcript detail error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <Loader message="Loading transcript..." />
      </div>
    );
  }

  if (error || !transcript) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h3>Error loading transcript</h3>
          <p>{error || 'Transcript not found'}</p>
          <button onClick={() => navigate('/transcripts')} className={styles.backButton}>
            Back to Transcripts
          </button>
        </div>
      </div>
    );
  }

  const { metadata, source, created_at, transcript: content } = transcript;

  const getWordCount = (text: string) => {
    return text.trim().split(/\s+/).length;
  };

  return (
    <div className={styles.container}>
      <button onClick={() => navigate('/transcripts')} className={styles.backButton}>
        ← Back to Transcripts
      </button>

      <header className={styles.header}>
        <div>
          <h1>{metadata?.title || 'Untitled Transcript'}</h1>
          <div className={styles.headerMeta}>
            <span className={`${styles.source} ${source === 's3' ? styles.sourceS3 : styles.sourceManual}`}>
              {source === 's3' ? 'S3 Import' : 'Manual Upload'}
            </span>
            <span className={styles.date}>
              Created: {formatISTFull(created_at)}
            </span>
          </div>
        </div>
      </header>

      {metadata?.description && (
        <section className={styles.section}>
          <h2>Description</h2>
          <p className={styles.description}>{metadata.description}</p>
        </section>
      )}

      {/* Statistics */}
      <section className={styles.section}>
        <h2>Statistics</h2>
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <div className={styles.statValue}>{getWordCount(content).toLocaleString()}</div>
            <div className={styles.statLabel}>Words</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statValue}>{content.length.toLocaleString()}</div>
            <div className={styles.statLabel}>Characters</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statValue}>{analyses.length}</div>
            <div className={styles.statLabel}>Analyses</div>
          </div>
        </div>
      </section>

      {/* Related Analyses */}
      {analyses.length > 0 && (
        <section className={styles.section}>
          <h2>Related Analyses</h2>
          <div className={styles.analysesList}>
            {analyses.map((analysis) => (
              <div
                key={analysis.uuid}
                className={styles.analysisItem}
                onClick={() => navigate(`/analysis/${analysis.uuid}`)}
              >
                <div className={styles.analysisHeader}>
                <span className={styles.analysisDate}>
                  {formatISTDate(analysis.created_at)}
                </span>
                  <span className={`${styles.analysisStatus} ${styles[`status${analysis.status.charAt(0).toUpperCase() + analysis.status.slice(1)}`]}`}>
                    {analysis.status}
                  </span>
                </div>
                {analysis.result && (
                  <div className={styles.analysisPreview}>
                    <span className={styles.previewLabel}>Sentiment:</span>
                    <span className={styles.previewValue}>{analysis.result.summary.overall_call_sentiment}</span>
                    <span className={styles.previewSeparator}>•</span>
                    <span className={styles.previewLabel}>Lead:</span>
                    <span className={styles.previewValue}>{analysis.result.summary.lead_temperature}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Transcript Content */}
      <section className={styles.section}>
        <h2>Full Transcript</h2>
        <div className={styles.transcriptBox}>
          <pre className={styles.transcriptText}>{content}</pre>
        </div>
      </section>
    </div>
  );
};

export default TranscriptDetail;
