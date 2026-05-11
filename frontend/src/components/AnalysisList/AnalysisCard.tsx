import type { Analysis } from '../../types/api.types';
import styles from './AnalysisList.module.scss';

interface AnalysisCardProps {
  analysis: Analysis;
  onClick: () => void;
}

const AnalysisCard = ({ analysis, onClick }: AnalysisCardProps) => {
  const { result, status, created_at, transcript, uuid } = analysis;

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Generate title with transcript name and short ID
  const getTitle = () => {
    console.log('xoxo -< >', analysis)
    const transcriptName = transcript?.metadata?.title || 'Untitled';
    const shortId = uuid.substring(0, 8);
    return `${transcriptName} (${shortId})`;
  };

  // Get status color
  const getStatusClass = () => {
    switch (status) {
      case 'success':
        return styles.statusSuccess;
      case 'failed':
        return styles.statusFailed;
      case 'processing':
        return styles.statusProcessing;
      default:
        return styles.statusPending;
    }
  };

  // Get sentiment color
  const getSentimentClass = (sentiment: string) => {
    const lower = sentiment.toLowerCase();
    if (lower.includes('positive')) return styles.sentimentPositive;
    if (lower.includes('negative')) return styles.sentimentNegative;
    return styles.sentimentNeutral;
  };

  // Get type badge
  const getTypeIcon = () => {
    return transcript?.type === 'digital' ? '🌐' : '🎤';
  };

  const getTypeLabel = () => {
    return transcript?.type === 'digital' ? 'Digital' : 'Voice';
  };

  return (
    <div className={styles.card} onClick={onClick}>
      <div className={styles.cardHeader} style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
        <div className={styles.cardTitle}>
          {getTitle()}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
          {transcript && (
            <div className={styles.typeBadge}>
              {getTypeIcon()} {getTypeLabel()}
            </div>
          )}
          <div className={`${styles.status} ${getStatusClass()}`}>
            {status}
          </div>
        </div>
      </div>

      {result && (
        <div className={styles.cardContent}>
          {/* Voice call metrics */}
          {result.summary?.overall_call_sentiment && (
            <>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Sentiment:</span>
                <span className={`${styles.metricValue} ${getSentimentClass(result.summary.overall_call_sentiment)}`}>
                  {result.summary.overall_call_sentiment}
                </span>
              </div>

              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Lead Temperature:</span>
                <span className={styles.metricValue}>
                  {result.summary.lead_temperature}
                </span>
              </div>

              <div className={styles.metricsGrid}>
                <div className={styles.miniMetric}>
                  <span className={styles.miniLabel}>Meeting</span>
                  <span className={styles.miniValue}>{result.summary.meeting_likelihood}%</span>
                </div>
                <div className={styles.miniMetric}>
                  <span className={styles.miniLabel}>Follow-up</span>
                  <span className={styles.miniValue}>{result.summary.follow_up_readiness}%</span>
                </div>
              </div>

              {result.notable_buying_signals && result.notable_buying_signals.length > 0 && (
                <div className={styles.signals}>
                  <span className={styles.signalBadge}>
                    {result.notable_buying_signals.length} Signal{result.notable_buying_signals.length !== 1 ? 's' : ''}
                  </span>
                </div>
              )}
            </>
          )}
          
          {/* Digital journey metrics */}
          {result.summary?.session_temperature && (
            <>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Session Temp:</span>
                <span className={styles.metricValue}>
                  {result.summary.session_temperature}
                </span>
              </div>

              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Journey Stage:</span>
                <span className={styles.metricValue}>
                  {result.summary.journey_stage}
                </span>
              </div>

              <div className={styles.metricsGrid}>
                <div className={styles.miniMetric}>
                  <span className={styles.miniLabel}>Conversion</span>
                  <span className={styles.miniValue}>{result.summary.conversion_readiness}%</span>
                </div>
                <div className={styles.miniMetric}>
                  <span className={styles.miniLabel}>Content</span>
                  <span className={styles.miniValue}>{result.summary.content_pieces_consumed}</span>
                </div>
              </div>

              {result.conversion_signals && result.conversion_signals.length > 0 && (
                <div className={styles.signals}>
                  <span className={styles.signalBadge}>
                    {result.conversion_signals.length} Signal{result.conversion_signals.length !== 1 ? 's' : ''}
                  </span>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {status === 'pending' && (
        <div className={styles.cardContent}>
          <p className={styles.pendingText}>Analysis pending...</p>
        </div>
      )}

      {status === 'failed' && (
        <div className={styles.cardContent}>
          <p className={styles.errorText}>Analysis failed</p>
        </div>
      )}

      <div className={styles.cardFooter}>
        <span className={styles.timestamp}>{formatDate(created_at)}</span>
      </div>
    </div>
  );
};

export default AnalysisCard;
