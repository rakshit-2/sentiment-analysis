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

interface SuccessRateChartProps {
  data: DetailedMetricData[];
}

const SuccessRateChart = ({ data }: SuccessRateChartProps) => {
  if (data.length === 0) {
    return (
      <div className={styles.emptyChart}>
        <p>No data available</p>
      </div>
    );
  }

  const chartData = data.map((day) => ({
    date: day.date,
    rate: day.success_rate,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="date" stroke="#666" style={{ fontSize: '11px' }} interval="preserveStartEnd" />
        <YAxis stroke="#666" style={{ fontSize: '11px' }} domain={[0, 100]} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            fontSize: '12px',
          }}
          formatter={(value) => [`${value}%`, 'Success Rate']}
        />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
        <Line
          type="monotone"
          dataKey="rate"
          stroke="#8b5cf6"
          strokeWidth={2}
          dot={{ fill: '#8b5cf6', r: 4 }}
          activeDot={{ r: 6 }}
          name="Success Rate (%)"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default SuccessRateChart;
