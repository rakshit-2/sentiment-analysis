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

  // Format the week label for display
  const formatWeek = (week: string) => {
    return week; // Can be customized further if needed
  };

  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis
          dataKey="week"
          tickFormatter={formatWeek}
          stroke="#666"
          style={{ fontSize: '12px' }}
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
          labelFormatter={(label) => `Week: ${label}`}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="count"
          stroke="#4a90e2"
          strokeWidth={2}
          dot={{ fill: '#4a90e2', r: 4 }}
          activeDot={{ r: 6 }}
          name="Analyses"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TrendsChart;
