import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { DetailedMetricData } from '../../types/api.types';
import styles from './Dashboard.module.scss';

interface FollowUpReadinessChartProps {
  data: DetailedMetricData[];
}

const FollowUpReadinessChart = ({ data }: FollowUpReadinessChartProps) => {
  if (data.length === 0) {
    return (
      <div className={styles.emptyChart}>
        <p>No data available</p>
      </div>
    );
  }

  const chartData = data.map((week) => ({
    week: week.week,
    readiness: week.averages.follow_up_readiness,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="week" stroke="#666" style={{ fontSize: '11px' }} />
        <YAxis stroke="#666" style={{ fontSize: '11px' }} domain={[0, 100]} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            fontSize: '12px',
          }}
          formatter={(value) => [`${value}%`, 'Readiness']}
        />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
        <Line
          type="monotone"
          dataKey="readiness"
          stroke="#10b981"
          strokeWidth={2}
          dot={{ fill: '#10b981', r: 4 }}
          activeDot={{ r: 6 }}
          name="Follow-up Readiness (%)"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default FollowUpReadinessChart;
