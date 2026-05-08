import { useState } from 'react';
import { triggerApi } from '../../services/api';
import styles from './Settings.module.scss';

const TriggerAnalysisTab = () => {
  const [batchSize, setBatchSize] = useState<number>(5);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{
    message: string;
    task_id: string;
    batch_size: number;
    status: string;
    monitor_url: string;
  } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setTriggering(true);
      setError(null);
      setSuccess(null);

      const result = await triggerApi.triggerAnalysis(batchSize);
      setSuccess(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger analysis');
    } finally {
      setTriggering(false);
    }
  };

  const handleReset = () => {
    setBatchSize(5);
    setError(null);
    setSuccess(null);
  };

  return (
    <div className={styles.tabPanel}>
      <h2>Trigger Analysis</h2>
      <p className={styles.description}>
        Manually trigger the analysis job to process unprocessed transcripts.
        This will queue a Celery task to analyze transcripts in the background.
      </p>

      <form onSubmit={handleSubmit} className={styles.form}>
        {/* Batch Size */}
        <div className={styles.formGroup}>
          <label htmlFor="batchSize">
            Batch Size
            <span className={styles.optional}> (optional, default: 5)</span>
          </label>
          <input
            id="batchSize"
            type="number"
            min="1"
            max="100"
            value={batchSize}
            onChange={(e) => setBatchSize(parseInt(e.target.value) || 5)}
            className={styles.input}
          />
          <small className={styles.helpText}>
            Number of unprocessed transcripts to analyze (1-100)
          </small>
        </div>

        {/* Info Box */}
        <div className={styles.infoBox}>
          <strong>ℹ️ How it works:</strong>
          <ul>
            <li>Finds unprocessed transcripts in the database</li>
            <li>Queues them for sentiment analysis using Celery</li>
            <li>Process runs in the background</li>
            <li>You can monitor progress at <a href="http://localhost:5555" target="_blank" rel="noopener noreferrer">Flower UI</a></li>
          </ul>
        </div>

        {/* Error Message */}
        {error && (
          <div className={styles.errorMessage}>
            ❌ {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className={styles.successMessage}>
            ✅ Analysis task queued successfully!
            <div className={styles.taskInfo}>
              <div><strong>Task ID:</strong> <code>{success.task_id}</code></div>
              <div><strong>Batch Size:</strong> {success.batch_size}</div>
              <div><strong>Status:</strong> <span className={styles.statusBadge}>{success.status}</span></div>
              <div>
                <strong>Monitor:</strong>{' '}
                <a 
                  href={success.monitor_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className={styles.monitorLink}
                >
                  View in Flower UI →
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Buttons */}
        <div className={styles.formActions}>
          <button
            type="submit"
            disabled={triggering}
            className={styles.submitButton}
          >
            {triggering ? 'Triggering...' : 'Trigger Analysis'}
          </button>
          <button
            type="button"
            onClick={handleReset}
            disabled={triggering}
            className={styles.resetButton}
          >
            Reset
          </button>
        </div>
      </form>
    </div>
  );
};

export default TriggerAnalysisTab;
