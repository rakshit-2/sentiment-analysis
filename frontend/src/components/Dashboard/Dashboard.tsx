import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisApi } from '../../services/api';
import type { Analysis, TrendData, DetailedMetricData } from '../../types/api.types';
import AnalysisCard from './AnalysisCard';
import TrendsChart from './TrendsChart';
import LeadTemperaturePieChart from './LeadTemperaturePieChart';
import SentimentChart from './SentimentChart';
import MeetingLikelihoodChart from './MeetingLikelihoodChart';
import FollowUpReadinessChart from './FollowUpReadinessChart';
import SuccessRateChart from './SuccessRateChart';
import styles from './Dashboard.module.scss';

const Dashboard = () => {
  const navigate = useNavigate();
  const [recentAnalyses, setRecentAnalyses] = useState<Analysis[]>([]);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [detailedMetrics, setDetailedMetrics] = useState<DetailedMetricData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch recent analyses, trends, and detailed metrics in parallel
      const [recentData, trendsData, detailedMetricsData] = await Promise.all([
        analysisApi.getRecent(24),
        analysisApi.getTrends(8),
        analysisApi.getDetailedMetrics(8),
      ]);

      setRecentAnalyses(recentData.analyses);
      setTrends(trendsData.data);
      setDetailedMetrics(detailedMetricsData.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCardClick = (analysisUuid: string) => {
    navigate(`/analysis/${analysisUuid}`, { state: { from: '/dashboard' } });
  };

  if (loading) {
    return (
      <div className={styles.dashboard}>
        <div className={styles.loading}>Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.dashboard}>
        <div className={styles.error}>
          <h3>Error loading dashboard</h3>
          <p>{error}</p>
          <button onClick={loadDashboardData} className={styles.retryButton}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>

      {/* Trends Chart Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2>Weekly Trends</h2>
          <p className={styles.sectionSubtitle}>Analysis activity over the past 8 weeks</p>
        </div>
        <div className={styles.chartContainer}>
          <TrendsChart data={trends} />
        </div>
      </section>

      {/* Detailed Metrics Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2>Detailed Metrics</h2>
          <p className={styles.sectionSubtitle}>Insights from analysis results over time</p>
        </div>
        
        {/* Row 1: Lead Temperature + Sentiment Distribution */}
        <div className={styles.metricsRow}>
          <div className={styles.metricCard}>
            <h3>Lead Temperature Distribution</h3>
            <LeadTemperaturePieChart data={detailedMetrics} />
          </div>
          
          <div className={styles.metricCard}>
            <h3>Sentiment Distribution</h3>
            <SentimentChart data={detailedMetrics} />
          </div>
        </div>
        
        {/* Row 2: Meeting Likelihood + Follow-up Readiness */}
        <div className={styles.metricsRow}>
          <div className={styles.metricCard}>
            <h3>Meeting Likelihood</h3>
            <MeetingLikelihoodChart data={detailedMetrics} />
          </div>
          
          <div className={styles.metricCard}>
            <h3>Follow-up Readiness</h3>
            <FollowUpReadinessChart data={detailedMetrics} />
          </div>
        </div>
        
        {/* Row 3: Success Rate (Full Width) */}
        <div className={styles.metricCardFull}>
          <h3>Success Rate</h3>
          <SuccessRateChart data={detailedMetrics} />
        </div>
      </section>

      {/* Recent Analyses Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2>Recent Analyses</h2>
          <p className={styles.sectionSubtitle}>
            {recentAnalyses.length} {recentAnalyses.length === 1 ? 'analysis' : 'analyses'} in the last 24 hours
          </p>
        </div>

        {recentAnalyses.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No analyses found in the last 24 hours</p>
          </div>
        ) : (
          <div className={styles.cardGrid}>
            {recentAnalyses.map((analysis) => (
              <AnalysisCard
                key={analysis.uuid}
                analysis={analysis}
                onClick={() => handleCardClick(analysis.uuid)}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default Dashboard;
