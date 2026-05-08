import { useState } from 'react';
import {
  BarChart,
  Bar,
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

interface SelectableMetricChartProps {
  data: DetailedMetricData[];
}

type MetricType = 'sentiment' | 'meeting' | 'followup' | 'success';

const SelectableMetricChart = ({ data }: SelectableMetricChartProps) => {
  const [selectedMetric, setSelectedMetric] = useState<MetricType>('sentiment');

  if (data.length === 0) {
    return (
      <div className={styles.emptyChart}>
        <p>No metrics data available</p>
      </div>
    );
  }

  const renderSentimentChart = () => {
    const chartData = data.map((week) => ({
      week: week.week,
      Positive: week.sentiment.positive,
      Negative: week.sentiment.negative,
      Neutral: week.sentiment.neutral,
      Mixed: week.sentiment.mixed,
    }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis dataKey="week" stroke="#666" style={{ fontSize: '12px' }} />
          <YAxis stroke="#666" style={{ fontSize: '12px' }} allowDecimals={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e0e0e0',
              borderRadius: '4px',
            }}
          />
          <Legend />
          <Bar dataKey="Positive" stackId="a" fill="#2d7a4f" />
          <Bar dataKey="Neutral" stackId="a" fill="#9ca3af" />
          <Bar dataKey="Mixed" stackId="a" fill="#f59e0b" />
          <Bar dataKey="Negative" stackId="a" fill="#c82333" />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderMeetingLikelihoodChart = () => {
    const chartData = data.map((week) => ({
      week: week.week,
      likelihood: week.averages.meeting_likelihood,
    }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis dataKey="week" stroke="#666" style={{ fontSize: '12px' }} />
          <YAxis stroke="#666" style={{ fontSize: '12px' }} domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e0e0e0',
              borderRadius: '4px',
            }}
            formatter={(value) => [`${value}%`, 'Likelihood']}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="likelihood"
            stroke="#4a90e2"
            strokeWidth={2}
            dot={{ fill: '#4a90e2', r: 4 }}
            activeDot={{ r: 6 }}
            name="Meeting Likelihood (%)"
          />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  const renderFollowUpChart = () => {
    const chartData = data.map((week) => ({
      week: week.week,
      readiness: week.averages.follow_up_readiness,
    }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis dataKey="week" stroke="#666" style={{ fontSize: '12px' }} />
          <YAxis stroke="#666" style={{ fontSize: '12px' }} domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e0e0e0',
              borderRadius: '4px',
            }}
            formatter={(value) => [`${value}%`, 'Readiness']}
          />
          <Legend />
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

  const renderSuccessRateChart = () => {
    const chartData = data.map((week) => ({
      week: week.week,
      rate: week.success_rate,
    }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis dataKey="week" stroke="#666" style={{ fontSize: '12px' }} />
          <YAxis stroke="#666" style={{ fontSize: '12px' }} domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e0e0e0',
              borderRadius: '4px',
            }}
            formatter={(value) => [`${value}%`, 'Success Rate']}
          />
          <Legend />
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

  return (
    <div>
      <div className={styles.metricSelector}>
        <label htmlFor="metric-select">Select Metric:</label>
        <select
          id="metric-select"
          value={selectedMetric}
          onChange={(e) => setSelectedMetric(e.target.value as MetricType)}
          className={styles.metricSelect}
        >
          <option value="sentiment">Sentiment Distribution</option>
          <option value="meeting">Average Meeting Likelihood</option>
          <option value="followup">Average Follow-up Readiness</option>
          <option value="success">Success Rate</option>
        </select>
      </div>

      {selectedMetric === 'sentiment' && renderSentimentChart()}
      {selectedMetric === 'meeting' && renderMeetingLikelihoodChart()}
      {selectedMetric === 'followup' && renderFollowUpChart()}
      {selectedMetric === 'success' && renderSuccessRateChart()}
    </div>
  );
};

export default SelectableMetricChart;
