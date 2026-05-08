import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { DetailedMetricData } from '../../types/api.types';
import styles from './Dashboard.module.scss';

interface SentimentChartProps {
  data: DetailedMetricData[];
}

const SentimentChart = ({ data }: SentimentChartProps) => {
  if (data.length === 0) {
    return (
      <div className={styles.emptyChart}>
        <p>No data available</p>
      </div>
    );
  }

  const chartData = data.map((week) => ({
    week: week.week,
    Positive: week.sentiment.positive,
    Negative: week.sentiment.negative,
    Neutral: week.sentiment.neutral,
    Mixed: week.sentiment.mixed,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="week" stroke="#666" style={{ fontSize: '11px' }} />
        <YAxis stroke="#666" style={{ fontSize: '11px' }} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            fontSize: '12px',
          }}
        />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
        <Bar dataKey="Positive" stackId="a" fill="#2d7a4f" />
        <Bar dataKey="Neutral" stackId="a" fill="#9ca3af" />
        <Bar dataKey="Mixed" stackId="a" fill="#f59e0b" />
        <Bar dataKey="Negative" stackId="a" fill="#c82333" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default SentimentChart;
