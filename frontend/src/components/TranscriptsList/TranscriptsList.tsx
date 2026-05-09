import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { transcriptApi } from '../../services/api';
import type { Transcript } from '../../types/api.types';
import TranscriptCard from './TranscriptCard';
import Loader from '../Loader';
import styles from './TranscriptsList.module.scss';

const ITEMS_PER_PAGE = 12;

const TranscriptsList = () => {
  const navigate = useNavigate();
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sourceFilter, setSourceFilter] = useState<string>('');

  useEffect(() => {
    loadTranscripts();
  }, [currentPage, sourceFilter]);

  const loadTranscripts = async () => {
    try {
      setLoading(true);
      setError(null);

      const skip = (currentPage - 1) * ITEMS_PER_PAGE;
      const allTranscripts = await transcriptApi.list({
        skip,
        limit: ITEMS_PER_PAGE,
        source: sourceFilter || undefined,
      });

      setTranscripts(allTranscripts);
      
      // Calculate total pages
      if (allTranscripts.length === ITEMS_PER_PAGE) {
        setTotalPages(currentPage + 1);
      } else {
        setTotalPages(currentPage);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load transcripts');
      console.error('Transcripts list error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCardClick = (transcriptUuid: string) => {
    navigate(`/transcripts/${transcriptUuid}`);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFilterChange = (source: string) => {
    setSourceFilter(source);
    setCurrentPage(1);
  };

  if (loading && currentPage === 1) {
    return (
      <div className={styles.container}>
        <Loader message="Loading transcripts..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h3>Error loading transcripts</h3>
          <p>{error}</p>
          <button onClick={loadTranscripts} className={styles.retryButton}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1>All Transcripts</h1>
          <p className={styles.subtitle}>Browse and manage all conversation transcripts</p>
        </div>
      </header>

      {/* Filters */}
      <div className={styles.filters}>
        <label htmlFor="source-filter">Filter by source:</label>
        <select
          id="source-filter"
          value={sourceFilter}
          onChange={(e) => handleFilterChange(e.target.value)}
          className={styles.filterSelect}
        >
          <option value="">All Sources</option>
          <option value="manual">Manual Upload</option>
          <option value="s3">S3 Import</option>
        </select>
      </div>

      {/* Transcripts Grid */}
      {transcripts.length === 0 ? (
        <div className={styles.emptyState}>
          <p>No transcripts found</p>
          {sourceFilter && (
            <button onClick={() => handleFilterChange('')} className={styles.clearFilterButton}>
              Clear Filter
            </button>
          )}
        </div>
      ) : (
        <>
          <div className={styles.cardGrid}>
            {transcripts.map((transcript) => (
              <TranscriptCard
                key={transcript.uuid}
                transcript={transcript}
                onClick={() => handleCardClick(transcript.uuid)}
              />
            ))}
          </div>

          {/* Pagination */}
          <div className={styles.pagination}>
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1 || loading}
              className={styles.paginationButton}
            >
              Previous
            </button>
            
            <span className={styles.pageInfo}>
              Page {currentPage} {totalPages > currentPage && `of ${totalPages}+`}
            </span>
            
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={transcripts.length < ITEMS_PER_PAGE || loading}
              className={styles.paginationButton}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default TranscriptsList;
