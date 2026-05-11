import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { DetailedMetricData } from '../../types/api.types';
import styles from './Dashboard.module.scss';

interface LeadTemperaturePieChartProps {
  data: DetailedMetricData[];
}

// Predefined colors for common temperature values
const TEMPERATURE_COLORS: Record<string, string> = {
  hot: '#ff6b6b',
  warm: '#ffd93d',
  cold: '#6bcfff',
  'very hot': '#dc143c',
  'very warm': '#ffb347',
  'very cold': '#4169e1',
  lukewarm: '#f5deb3',
  neutral: '#a9a9a9',
};

// Generate a color for unknown temperature values
const generateColor = (index: number): string => {
  const colors = [
    '#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', 
    '#a4de6c', '#d0ed57', '#83a6ed', '#8dd1e1'
  ];
  return colors[index % colors.length];
};

const LeadTemperaturePieChart = ({ data }: LeadTemperaturePieChartProps) => {
  if (data.length === 0) {
    return (
      <div className={styles.emptyChart}>
        <p>No temperature data available</p>
      </div>
    );
  }

  // Dynamically aggregate all temperature values from both voice and digital
  const totals: Record<string, number> = {};
  
  data.forEach(week => {
    // Handle voice transcripts (lead_temperature)
    const leadTemps = week.lead_temperature;
    if (leadTemps && typeof leadTemps === 'object') {
      Object.entries(leadTemps).forEach(([key, value]) => {
        if (typeof value === 'number') {
          totals[key] = (totals[key] || 0) + value;
        }
      });
    }
    
    // Handle digital transcripts (session_temperature)
    const sessionTemps = week.session_temperature;
    if (sessionTemps && typeof sessionTemps === 'object') {
      Object.entries(sessionTemps).forEach(([key, value]) => {
        if (typeof value === 'number') {
          totals[key] = (totals[key] || 0) + value;
        }
      });
    }
  });

  // Convert to chart data format and filter out zero values
  const chartData = Object.entries(totals)
    .map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1), // Capitalize first letter
      value: value,
      key: name.toLowerCase()
    }))
    .filter(item => item.value > 0)
    .sort((a, b) => b.value - a.value); // Sort by value descending

  if (chartData.length === 0) {
    return (
      <div className={styles.emptyChart}>
        <p>No temperature data available</p>
      </div>
    );
  }

  // Get color for each entry
  const getColor = (key: string, index: number): string => {
    return TEMPERATURE_COLORS[key] || generateColor(index);
  };

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
          {chartData.map((entry, index) => (
            <Cell
              key={`cell-${entry.key}`}
              fill={getColor(entry.key, index)}
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
