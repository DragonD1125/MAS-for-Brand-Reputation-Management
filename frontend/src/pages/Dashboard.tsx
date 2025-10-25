import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Error,
  Timeline,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { monitoringApi, analyticsApi } from '../services/api';
import { toast } from 'react-toastify';

interface MetricsData {
  total_mentions: number;
  sentiment_score: number;
  crisis_alerts: number;
  processed_today: number;
  autonomous_actions: number;
  hitl_pending: number;
}

interface SentimentTrend {
  timestamp: string;
  positive: number;
  negative: number;
  neutral: number;
  overall_score: number;
}

const Dashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState('24h');

  // Fetch real-time metrics
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => monitoringApi.getMetrics().then(res => res.data),
    refetchInterval: 30000, // Refetch every 30 seconds
    onError: () => toast.error('Failed to fetch metrics')
  });

  // Fetch sentiment trends
  const { data: sentimentTrends, isLoading: trendsLoading } = useQuery({
    queryKey: ['sentiment-trends', timeRange],
    queryFn: () => analyticsApi.getSentimentTrends({ range: timeRange }).then(res => res.data),
    refetchInterval: 60000, // Refetch every minute
    onError: () => toast.error('Failed to fetch sentiment trends')
  });

  // Fetch system health
  const { data: systemHealth, isLoading: healthLoading } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => monitoringApi.getSystemHealth().then(res => res.data),
    refetchInterval: 15000, // Refetch every 15 seconds
  });

  if (metricsError) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to connect to the autonomous system. Please check if the backend is running.
        </Alert>
      </Box>
    );
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const formatSentimentData = (trends: SentimentTrend[]) => {
    if (!trends) return [];
    return trends.map(trend => ({
      time: new Date(trend.timestamp).toLocaleDateString(),
      positive: trend.positive,
      negative: trend.negative,
      neutral: trend.neutral,
      score: trend.overall_score,
    }));
  };

  const MetricCard = ({ title, value, icon, trend, color = 'primary' }: any) => (
    <Card sx={{ height: '100%', bgcolor: 'background.paper' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={color}>
              {metricsLoading ? <CircularProgress size={24} /> : value}
            </Typography>
          </Box>
          <Box display="flex" flexDirection="column" alignItems="center">
            {icon}
            {trend && (
              <Box display="flex" alignItems="center" mt={1}>
                {trend > 0 ? <TrendingUp color="success" /> : <TrendingDown color="error" />}
                <Typography variant="caption" color={trend > 0 ? 'success.main' : 'error.main'}>
                  {Math.abs(trend)}%
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Autonomous System Dashboard
        </Typography>
        <Box display="flex" gap={1}>
          <Chip
            label={systemHealth?.status || 'Unknown'}
            color={systemHealth?.status === 'healthy' ? 'success' : 'error'}
            icon={systemHealth?.status === 'healthy' ? <CheckCircle /> : <Error />}
          />
        </Box>
      </Box>

      {/* Real-time Metrics Grid */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={2}>
          <MetricCard
            title="Total Mentions"
            value={metrics?.total_mentions || 0}
            icon={<Timeline color="primary" />}
            trend={5.2}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <MetricCard
            title="Sentiment Score"
            value={metrics?.sentiment_score ? `${(metrics.sentiment_score * 100).toFixed(1)}%` : '0%'}
            icon={<TrendingUp color="success" />}
            trend={2.1}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <MetricCard
            title="Crisis Alerts"
            value={metrics?.crisis_alerts || 0}
            icon={<Warning color="warning" />}
            trend={-10.5}
            color="warning.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <MetricCard
            title="Processed Today"
            value={metrics?.processed_today || 0}
            icon={<CheckCircle color="info" />}
            trend={15.3}
            color="info.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <MetricCard
            title="Autonomous Actions"
            value={metrics?.autonomous_actions || 0}
            icon={<Timeline color="secondary" />}
            trend={8.7}
            color="secondary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <MetricCard
            title="HITL Pending"
            value={metrics?.hitl_pending || 0}
            icon={<Warning color="error" />}
            color="error.main"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Sentiment Trends Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Sentiment Trends (24h)
            </Typography>
            {trendsLoading ? (
              <Box display="flex" justifyContent="center" alignItems="center" height={300}>
                <CircularProgress />
              </Box>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={formatSentimentData(sentimentTrends)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="positive"
                    stackId="1"
                    stroke="#4caf50"
                    fill="#4caf50"
                    fillOpacity={0.6}
                  />
                  <Area
                    type="monotone"
                    dataKey="neutral"
                    stackId="1"
                    stroke="#ff9800"
                    fill="#ff9800"
                    fillOpacity={0.6}
                  />
                  <Area
                    type="monotone"
                    dataKey="negative"
                    stackId="1"
                    stroke="#f44336"
                    fill="#f44336"
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            {healthLoading ? (
              <Box display="flex" justifyContent="center" alignItems="center" height={300}>
                <CircularProgress />
              </Box>
            ) : (
              <Box>
                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary">
                    AI Agents Status
                  </Typography>
                  <Box display="flex" gap={1} mt={1}>
                    <Chip label="Data Collection" color="success" size="small" />
                    <Chip label="Sentiment Analysis" color="success" size="small" />
                    <Chip label="Alert Management" color="success" size="small" />
                  </Box>
                </Box>
                
                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary">
                    Last Action
                  </Typography>
                  <Typography variant="body1">
                    Processed 15 new mentions
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    2 minutes ago
                  </Typography>
                </Box>

                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary">
                    API Response Time
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    {systemHealth?.response_time_ms || 0}ms
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="body2" color="textSecondary">
                    Memory Usage
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1}>
                    <CircularProgress
                      variant="determinate"
                      value={systemHealth?.memory_usage_percent || 0}
                      size={24}
                    />
                    <Typography variant="body2">
                      {systemHealth?.memory_usage_percent || 0}%
                    </Typography>
                  </Box>
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Recent Activity Feed */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Autonomous Actions
            </Typography>
            <Box>
              {[1, 2, 3, 4, 5].map((item) => (
                <Box key={item} display="flex" alignItems="center" gap={2} p={1} borderBottom="1px solid rgba(255,255,255,0.1)">
                  <CheckCircle color="success" fontSize="small" />
                  <Box flexGrow={1}>
                    <Typography variant="body2">
                      Analyzed mention from @user{item} - Sentiment: Positive
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {item} minutes ago
                    </Typography>
                  </Box>
                  <Chip label="Autonomous" size="small" color="secondary" />
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
