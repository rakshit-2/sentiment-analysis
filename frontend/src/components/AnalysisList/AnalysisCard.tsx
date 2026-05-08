import type { Analysis } from '../../types/api.types';
import styles from './AnalysisList.module.scss';

interface AnalysisCardProps {
  analysis: Analysis;
  onClick: () => void;
}

const AnalysisCard = ({ analysis, onClick }: AnalysisCardProps) => {
  const { result, status, created_at, transcript } = analysis;

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

  return (
    <div className={styles.card} onClick={onClick}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>
          {transcript?.metadata?.title || 'Untitled Analysis'}
        </div>
        <div className={`${styles.status} ${getStatusClass()}`}>
          {status}
        </div>
      </div>

      {result && (
        <div className={styles.cardContent}>
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

          {result.notable_buying_signals.length > 0 && (
            <div className={styles.signals}>
              <span className={styles.signalBadge}>
                {result.notable_buying_signals.length} Signal{result.notable_buying_signals.length !== 1 ? 's' : ''}
              </span>
            </div>
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
