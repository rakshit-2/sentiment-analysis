import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisApi } from '../../services/api';
import type { Analysis } from '../../types/api.types';
import AnalysisCard from './AnalysisCard';
import Loader from '../Loader';
import styles from './AnalysisList.module.scss';

const ITEMS_PER_PAGE = 12;

const AnalysisList = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAnalyses();
  }, [currentPage, statusFilter]);

  const loadAnalyses = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const skip = (currentPage - 1) * ITEMS_PER_PAGE;
      const allAnalyses = await analysisApi.list({
        skip,
        limit: ITEMS_PER_PAGE,
        status: statusFilter || undefined,
      });

      setAnalyses(allAnalyses);
      
      // Calculate total pages (this is an approximation since we don't have total count from API)
      // If we got a full page, there might be more pages
      if (allAnalyses.length === ITEMS_PER_PAGE) {
        setTotalPages(currentPage + 1);
      } else {
        setTotalPages(currentPage);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analyses');
      console.error('Analysis list error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadAnalyses(true);
  };

  const handleCardClick = (analysisUuid: string) => {
    navigate(`/analysis/${analysisUuid}`, { state: { from: '/analysis' } });
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFilterChange = (status: string) => {
    setStatusFilter(status);
    setCurrentPage(1); // Reset to first page when filter changes
  };

  if (loading && currentPage === 1) {
    return (
      <div className={styles.container}>
        <Loader message="Loading analyses..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h3>Error loading analyses</h3>
          <p>{error}</p>
          <button onClick={() => loadAnalyses()} className={styles.retryButton}>
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
          <h1>All Analyses</h1>
          <p className={styles.subtitle}>Browse and explore all sentiment analyses</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className={styles.refreshButton}
          title="Refresh analyses"
        >
          {refreshing ? '↻ Refreshing...' : '↻ Refresh'}
        </button>
      </header>

      {/* Filters */}
      <div className={styles.filters}>
        <label htmlFor="status-filter">Filter by status:</label>
        <select
          id="status-filter"
          value={statusFilter}
          onChange={(e) => handleFilterChange(e.target.value)}
          className={styles.filterSelect}
        >
          <option value="">All Statuses</option>
          <option value="success">Success</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Analysis Grid */}
      {analyses.length === 0 ? (
        <div className={styles.emptyState}>
          <p>No analyses found</p>
          {statusFilter && (
            <button onClick={() => handleFilterChange('')} className={styles.clearFilterButton}>
              Clear Filter
            </button>
          )}
        </div>
      ) : (
        <>
          <div className={styles.cardGrid}>
            {analyses.map((analysis) => (
              <AnalysisCard
                key={analysis.uuid}
                analysis={analysis}
                onClick={() => handleCardClick(analysis.uuid)}
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
              disabled={analyses.length < ITEMS_PER_PAGE || loading}
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

export default AnalysisList;
