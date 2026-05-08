import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { DetailedMetricData } from '../../types/api.types';
import styles from './Dashboard.module.scss';

interface LeadTemperaturePieChartProps {
  data: DetailedMetricData[];
}

const COLORS = {
  hot: '#ff6b6b',
  warm: '#ffd93d',
  cold: '#6bcfff',
};

const LeadTemperaturePieChart = ({ data }: LeadTemperaturePieChartProps) => {
  if (data.length === 0) {
    return (
      <div className={styles.emptyChart}>
        <p>No lead temperature data available</p>
      </div>
    );
  }

  // Aggregate all lead temperature counts
  const totals = data.reduce(
    (acc, week) => ({
      hot: acc.hot + week.lead_temperature.hot,
      warm: acc.warm + week.lead_temperature.warm,
      cold: acc.cold + week.lead_temperature.cold,
    }),
    { hot: 0, warm: 0, cold: 0 }
  );

  const chartData = [
    { name: 'Hot', value: totals.hot },
    { name: 'Warm', value: totals.warm },
    { name: 'Cold', value: totals.cold },
  ].filter(item => item.value > 0); // Only show categories with data

  if (chartData.length === 0) {
    return (
      <div className={styles.emptyChart}>
        <p>No lead temperature data available</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {chartData.map((entry) => (
            <Cell
              key={`cell-${entry.name}`}
              fill={COLORS[entry.name.toLowerCase() as keyof typeof COLORS]}
            />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default LeadTemperaturePieChart;
