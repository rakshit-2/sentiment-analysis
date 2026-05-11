import type { Transcript } from '../../types/api.types';
import styles from './TranscriptsList.module.scss';

interface TranscriptCardProps {
  transcript: Transcript;
  onClick: () => void;
}

const TranscriptCard = ({ transcript, onClick }: TranscriptCardProps) => {
  const { metadata, source, type, created_at, transcript: content } = transcript;

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

  // Get word count
  const getWordCount = (text: string) => {
    return text.trim().split(/\s+/).length;
  };

  // Get preview text
  const getPreviewText = (text: string, maxLength: number = 150) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
  };

  // Get source badge color
  const getSourceClass = () => {
    return source === 's3' ? styles.sourceS3 : styles.sourceManual;
  };

  // Get type badge
  const getTypeIcon = () => {
    return type === 'digital' ? '🌐' : '🎤';
  };

  const getTypeLabel = () => {
    return type === 'digital' ? 'Digital' : 'Voice';
  };

  return (
    <div className={styles.card} onClick={onClick}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>
          {metadata?.title || 'Untitled Transcript'}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <div className={styles.typeBadge}>
            {getTypeIcon()} {getTypeLabel()}
          </div>
          <div className={`${styles.source} ${getSourceClass()}`}>
            {source === 's3' ? 'S3' : 'Manual'}
          </div>
        </div>
      </div>

      <div className={styles.cardContent}>
        {metadata?.description && (
          <p className={styles.description}>{metadata.description}</p>
        )}
        
        <div className={styles.preview}>
          <p className={styles.previewText}>{getPreviewText(content)}</p>
        </div>

        <div className={styles.stats}>
          <div className={styles.stat}>
            <span className={styles.statLabel}>Words</span>
            <span className={styles.statValue}>{getWordCount(content).toLocaleString()}</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statLabel}>Characters</span>
            <span className={styles.statValue}>{content.length.toLocaleString()}</span>
          </div>
        </div>
      </div>

      <div className={styles.cardFooter}>
        <span className={styles.timestamp}>Created {formatDate(created_at)}</span>
      </div>
    </div>
  );
};

export default TranscriptCard;
