import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../services/api';

const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedBrand, setSelectedBrand] = useState('all');

  const { data: sentimentTrends, isLoading: trendsLoading } = useQuery({
    queryKey: ['sentiment-trends', timeRange],
    queryFn: () => analyticsApi.getSentimentTrends({ range: timeRange }).then(res => res.data),
    refetchInterval: 300000, // 5 minutes
  });

  const { data: crisisDetection, isLoading: crisisLoading } = useQuery({
    queryKey: ['crisis-detection'],
    queryFn: () => analyticsApi.getCrisisDetection().then(res => res.data),
    refetchInterval: 60000, // 1 minute for crisis detection
  });

  const { data: topKeywords, isLoading: keywordsLoading } = useQuery({
    queryKey: ['keywords', timeRange],
    queryFn: () => analyticsApi.getTopKeywords({ range: timeRange }).then(res => res.data),
  });

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  // Mock data for demonstration
  const platformData = [
    { name: 'Twitter', value: 45, color: '#1DA1F2' },
    { name: 'Facebook', value: 25, color: '#4267B2' },
    { name: 'Instagram', value: 20, color: '#E4405F' },
    { name: 'Reddit', value: 10, color: '#FF4500' },
  ];

  const hourlyActivity = Array.from({ length: 24 }, (_, i) => ({
    hour: i,
    mentions: Math.floor(Math.random() * 100) + 20,
    sentiment: (Math.random() - 0.5) * 2,
  }));

  const sentimentDistribution = [
    { name: 'Positive', value: 65, color: '#4CAF50' },
    { name: 'Neutral', value: 25, color: '#FF9800' },
    { name: 'Negative', value: 10, color: '#F44336' },
  ];

  const keywordTrends = topKeywords?.map((keyword: any, index: number) => ({
    keyword: keyword.word,
    mentions: keyword.count,
    sentiment: keyword.avg_sentiment,
    growth: keyword.growth_rate || Math.random() * 20 - 10,
  })) || [];

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Advanced Analytics
        </Typography>
        <Box display="flex" gap={2}>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="24h">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
            </Select>
          </FormControl>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Brand</InputLabel>
            <Select
              value={selectedBrand}
              label="Brand"
              onChange={(e) => setSelectedBrand(e.target.value)}
            >
              <MenuItem value="all">All Brands</MenuItem>
              <MenuItem value="brand1">Brand 1</MenuItem>
              <MenuItem value="brand2">Brand 2</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Sentiment Trends Over Time */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Sentiment Trends Over Time
            </Typography>
            {trendsLoading ? (
              <Box display="flex" justifyContent="center" alignItems="center" height={300}>
                <CircularProgress />
              </Box>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={sentimentTrends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis domain={[-1, 1]} />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="overall_score"
                    stroke="#2196F3"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="positive"
                    stroke="#4CAF50"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="negative"
                    stroke="#F44336"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>

        {/* Sentiment Distribution */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Sentiment Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sentimentDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sentimentDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Hourly Activity Heatmap */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              24-Hour Activity Pattern
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={hourlyActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="mentions" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Platform Distribution */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Platform Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={platformData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {platformData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Crisis Detection Status */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Crisis Detection Status
            </Typography>
            {crisisLoading ? (
              <Box display="flex" justifyContent="center" p={2}>
                <CircularProgress />
              </Box>
            ) : crisisDetection?.is_crisis ? (
              <Alert severity="error" sx={{ mb: 2 }}>
                <Typography variant="h6">CRISIS DETECTED</Typography>
                <Typography>
                  Risk Level: {crisisDetection.risk_level}
                </Typography>
                <Typography>
                  Confidence: {(crisisDetection.confidence * 100).toFixed(1)}%
                </Typography>
              </Alert>
            ) : (
              <Alert severity="success">
                <Typography variant="h6">All Clear</Typography>
                <Typography>No crisis indicators detected</Typography>
              </Alert>
            )}
            
            <Typography variant="body2" color="textSecondary">
              Last checked: {new Date().toLocaleTimeString()}
            </Typography>
          </Paper>
        </Grid>

        {/* Top Keywords */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Trending Keywords
            </Typography>
            {keywordsLoading ? (
              <Box display="flex" justifyContent="center" p={2}>
                <CircularProgress size={24} />
              </Box>
            ) : (
              <Box>
                {keywordTrends.slice(0, 10).map((keyword: any, index: number) => (
                  <Box
                    key={keyword.keyword}
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    p={1}
                    borderBottom="1px solid rgba(255,255,255,0.1)"
                  >
                    <Box>
                      <Typography variant="body1">
                        #{keyword.keyword}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {keyword.mentions} mentions
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography
                        variant="caption"
                        color={keyword.sentiment > 0 ? 'success.main' : keyword.sentiment < 0 ? 'error.main' : 'warning.main'}
                      >
                        {keyword.sentiment > 0 ? '↗' : keyword.sentiment < 0 ? '↘' : '→'}
                        {(keyword.sentiment * 100).toFixed(0)}%
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Keyword Growth Scatter Plot */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Keyword Performance Matrix (Mentions vs Sentiment)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart>
                <CartesianGrid />
                <XAxis 
                  type="number" 
                  dataKey="mentions" 
                  name="Mentions"
                  domain={['dataMin', 'dataMax']}
                />
                <YAxis 
                  type="number" 
                  dataKey="sentiment" 
                  name="Sentiment"
                  domain={[-1, 1]}
                />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter
                  name="Keywords"
                  data={keywordTrends}
                  fill="#8884d8"
                />
              </ScatterChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
