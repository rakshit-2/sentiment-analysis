import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { TrendData } from '../../types/api.types';
import styles from './Dashboard.module.scss';

interface TrendsChartProps {
  data: TrendData[];
}

const TrendsChart = ({ data }: TrendsChartProps) => {
  if (data.length === 0) {
    return (
      <div className={styles.emptyChart}>
        <p>No trend data available</p>
      </div>
    );
  }

  // Format the date label for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const month = date.toLocaleDateString('en-US', { month: 'short' });
    const day = date.getDate();
    return `${month} ${day}`;
  };

  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          stroke="#666"
          style={{ fontSize: '12px' }}
          interval="preserveStartEnd"
        />
        <YAxis
          stroke="#666"
          style={{ fontSize: '12px' }}
          allowDecimals={false}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
          }}
          labelFormatter={(label) => `Date: ${formatDate(label as string)}`}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="count"
          stroke="#4a90e2"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
          name="Analyses"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TrendsChart;
