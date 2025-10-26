import React, { useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Grid,
  Paper,
  Stack,
  TextField,
  Typography,
  Tabs,
  Tab,
  LinearProgress,
  Card,
  CardContent,
} from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { Pie, PieChart, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import LaunchIcon from '@mui/icons-material/Launch';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import InfoIcon from '@mui/icons-material/Info';
import ArticleIcon from '@mui/icons-material/Article';
import SchemaIcon from '@mui/icons-material/Schema';
import TimelineIcon from '@mui/icons-material/Timeline';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

import {
  analyticsApi,
  BrandAnalysisPayload,
  BrandAnalysisResponse,
} from '../services/api';

const sentimentColors: Record<string, string> = {
  positive: '#2e7d32',
  neutral: '#0288d1',
  negative: '#c62828',
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const Dashboard: React.FC = () => {
  const [brandName, setBrandName] = useState('Acme Corp');
  const [maxArticles, setMaxArticles] = useState(10);
  const [daysBack, setDaysBack] = useState(7);
  const [tabValue, setTabValue] = useState(0);

  const analysisMutation = useMutation<BrandAnalysisResponse, Error, BrandAnalysisPayload>({
    mutationFn: (payload) => analyticsApi.runBrandAnalysis(payload).then((res) => res.data),
  });

  const orchestrationMutation = useMutation<any, Error, BrandAnalysisPayload>({
    mutationFn: (payload) => analyticsApi.runOrchestration(payload).then((res) => res.data),
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!brandName.trim()) {
      return;
    }

    const payload = {
      brand_name: brandName.trim(),
      max_articles: Math.min(25, Math.max(3, maxArticles)),
      days_back: Math.min(30, Math.max(1, daysBack)),
    };

    if (tabValue === 0) {
      analysisMutation.mutate(payload);
    } else {
      orchestrationMutation.mutate(payload);
    }
  };

  const analysis = analysisMutation.data;
  const orchestration = orchestrationMutation.data;
  const isLoading = analysisMutation.isLoading || orchestrationMutation.isLoading;

  const sentimentBreakdown = useMemo(() => {
    if (!analysis) return [];
    return [
      { name: 'Positive', value: analysis.summary.positive, fill: sentimentColors.positive },
      { name: 'Neutral', value: analysis.summary.neutral, fill: sentimentColors.neutral },
      { name: 'Negative', value: analysis.summary.negative, fill: sentimentColors.negative },
    ];
  }, [analysis]);

  const orchestrationBreakdown = useMemo(() => {
    if (!orchestration) return [];
    return [
      {
        name: 'Positive',
        value: orchestration.summary.positive,
        fill: sentimentColors.positive,
      },
      { name: 'Neutral', value: orchestration.summary.neutral, fill: sentimentColors.neutral },
      {
        name: 'Negative',
        value: orchestration.summary.negative,
        fill: sentimentColors.negative,
      },
    ];
  }, [orchestration]);

  return (
    <Box p={{ xs: 2, md: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Run Brand Analysis
            </Typography>
            <Tabs
              value={tabValue}
              onChange={(_, newValue) => setTabValue(newValue)}
              sx={{ mb: 2, borderBottom: 1, borderColor: 'divider' }}
              aria-label="analysis tabs"
            >
              <Tab label="Quick Analysis" icon={<ArticleIcon />} iconPosition="start" />
              <Tab label="Full Orchestration" icon={<SchemaIcon />} iconPosition="start" />
            </Tabs>

            {tabValue === 0 && (
              <Typography variant="body2" color="text.secondary" mb={2}>
                Enter a brand to fetch the latest articles from NewsAPI and generate sentiment insights.
              </Typography>
            )}
            {tabValue === 1 && (
              <Typography variant="body2" color="text.secondary" mb={2}>
                Run all three agents (Data Collection, Sentiment Analysis, Response Generation) with full orchestration.
              </Typography>
            )}

            <Box component="form" onSubmit={handleSubmit} noValidate>
              <Stack spacing={2}>
                <TextField
                  label="Brand name"
                  value={brandName}
                  onChange={(event) => setBrandName(event.target.value)}
                  fullWidth
                  required
                />
                <TextField
                  label="Articles to fetch"
                  type="number"
                  value={maxArticles}
                  onChange={(event) => {
                    const value = Number(event.target.value);
                    setMaxArticles(Number.isNaN(value) ? 10 : value);
                  }}
                  inputProps={{ min: 3, max: 25 }}
                  fullWidth
                />
                <TextField
                  label="Days to look back"
                  type="number"
                  value={daysBack}
                  onChange={(event) => {
                    const value = Number(event.target.value);
                    setDaysBack(Number.isNaN(value) ? 7 : value);
                  }}
                  inputProps={{ min: 1, max: 30 }}
                  fullWidth
                />
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={isLoading}
                >
                  {isLoading ? 'Analyzing…' : tabValue === 0 ? 'Analyze Brand' : 'Run Orchestration'}
                </Button>
              </Stack>
            </Box>

            {analysisMutation.isError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {analysisMutation.error?.message || 'Analysis failed. Please try again.'}
              </Alert>
            )}
            {orchestrationMutation.isError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {orchestrationMutation.error?.message || 'Orchestration failed. Please try again.'}
              </Alert>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <TabPanel value={tabValue} index={0}>
            {/* Quick Analysis Tab */}
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Sentiment Overview
              </Typography>
              {isLoading && !analysis ? (
                <Box display="flex" justifyContent="center" alignItems="center" height={280}>
                  <CircularProgress />
                </Box>
              ) : analysis ? (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Box height={260}>
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={sentimentBreakdown}
                            dataKey="value"
                            nameKey="name"
                            innerRadius={60}
                          >
                            {sentimentBreakdown.map((entry, index) => (
                              <Cell key={`cell-${entry.name}`} fill={entry.fill} />
                            ))}
                          </Pie>
                          <Tooltip />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Stack spacing={1.5}>
                      <Typography variant="subtitle1" fontWeight={600}>
                        {analysis.brand_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Analysis ran at {new Date(analysis.fetched_at).toLocaleString()} covering
                        the last {analysis.timeframe_days} days.
                      </Typography>
                      <Chip
                        icon={
                          analysis.summary.average_sentiment_score >= 0 ? (
                            <TrendingUpIcon />
                          ) : (
                            <TrendingDownIcon />
                          )
                        }
                        label={`Average sentiment score: ${analysis.summary.average_sentiment_score.toFixed(2)}`}
                        color={
                          analysis.summary.average_sentiment_score >= 0 ? 'success' : 'error'
                        }
                      />
                      <Stack direction="row" spacing={1} flexWrap="wrap">
                        <Chip color="success" label={`Positive: ${analysis.summary.positive}`} />
                        <Chip color="info" label={`Neutral: ${analysis.summary.neutral}`} />
                        <Chip color="error" label={`Negative: ${analysis.summary.negative}`} />
                      </Stack>
                    </Stack>
                  </Grid>
                </Grid>
              ) : (
                <Box
                  height={260}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  sx={{ color: 'text.secondary' }}
                >
                  <Typography variant="body1">Run an analysis to see sentiment insights.</Typography>
                </Box>
              )}
            </Paper>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            {/* Full Orchestration Tab */}
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Multi-Agent Orchestration Results
              </Typography>
              {isLoading && !orchestration ? (
                <Box display="flex" justifyContent="center" alignItems="center" height={280}>
                  <Stack alignItems="center" spacing={2}>
                    <CircularProgress />
                    <Typography variant="body2">Running all 3 agents...</Typography>
                  </Stack>
                </Box>
              ) : orchestration ? (
                <Stack spacing={3}>
                  {/* Execution Summary */}
                  <Card variant="outlined">
                    <CardContent>
                      <Stack spacing={2}>
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="subtitle1" fontWeight={600}>
                            Workflow: {orchestration.workflow_id}
                          </Typography>
                          <Chip
                            icon={orchestration.success ? <CheckCircleIcon /> : <ErrorIcon />}
                            label={orchestration.success ? 'Success' : 'Failed'}
                            color={orchestration.success ? 'success' : 'error'}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Execution Time: {orchestration.execution_time_seconds.toFixed(2)}s
                        </Typography>
                        <Stack direction="row" spacing={1}>
                          {orchestration.steps_completed.map((step) => (
                            <Chip
                              key={step}
                              icon={<CheckCircleIcon />}
                              label={step.replace(/_/g, ' ')}
                              color="success"
                              size="small"
                            />
                          ))}
                        </Stack>
                      </Stack>
                    </CardContent>
                  </Card>

                  {/* Sentiment Breakdown */}
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Box height={260}>
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={orchestrationBreakdown}
                              dataKey="value"
                              nameKey="name"
                              innerRadius={60}
                            >
                              {orchestrationBreakdown.map((entry, index) => (
                                <Cell key={`cell-${entry.name}`} fill={entry.fill} />
                              ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                          </PieChart>
                        </ResponsiveContainer>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Stack spacing={1.5}>
                        <Typography variant="subtitle2" fontWeight={600}>
                          Sentiment Analysis Agent Results
                        </Typography>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Average Sentiment Score
                          </Typography>
                          <Typography variant="h6">
                            {orchestration.summary.average_sentiment_score.toFixed(2)}
                          </Typography>
                        </Box>
                        <Stack spacing={0.5}>
                          {orchestrationBreakdown.map((item) => (
                            <Box key={item.name} display="flex" justifyContent="space-between">
                              <Typography variant="body2">{item.name}</Typography>
                              <Typography variant="body2" fontWeight={500}>
                                {item.value}
                              </Typography>
                            </Box>
                          ))}
                        </Stack>
                      </Stack>
                    </Grid>
                  </Grid>

                  {/* Risk Assessment */}
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                        Risk Assessment & Crisis Analysis
                      </Typography>
                      <Stack spacing={1.5}>
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2">Crisis Score</Typography>
                          <Typography variant="body2" fontWeight={600}>
                            {orchestration.risk_assessments.crisis_score.toFixed(2)} / 1.00
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={orchestration.risk_assessments.crisis_score * 100}
                          sx={{
                            height: 8,
                            borderRadius: 1,
                            backgroundColor: '#e0e0e0',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor:
                                orchestration.risk_assessments.crisis_score > 0.6 ? '#c62828' : '#2e7d32',
                            },
                          }}
                        />
                        <Chip
                          label={`Level: ${orchestration.risk_assessments.crisis_level}`}
                          color={
                            orchestration.risk_assessments.crisis_level === 'severe'
                              ? 'error'
                              : orchestration.risk_assessments.crisis_level === 'moderate'
                              ? 'warning'
                              : 'success'
                          }
                          size="small"
                        />
                        <Typography variant="body2" color="text.secondary">
                          Negative Sentiment Ratio:{' '}
                          {(orchestration.risk_assessments.negative_sentiment_ratio * 100).toFixed(1)}%
                        </Typography>
                      </Stack>
                    </CardContent>
                  </Card>

                  {/* Recommendations */}
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                        Response Generation Agent - Recommendations
                      </Typography>
                      <Stack spacing={1}>
                        {orchestration.recommendations.map((rec, idx) => (
                          <Box key={idx} display="flex" gap={1} alignItems="flex-start">
                            <InfoIcon color="primary" sx={{ mt: 0.5, flexShrink: 0 }} />
                            <Typography variant="body2">{rec}</Typography>
                          </Box>
                        ))}
                      </Stack>
                    </CardContent>
                  </Card>

                  {/* Next Actions */}
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                        Next Actions
                      </Typography>
                      <Stack spacing={1}>
                        {orchestration.next_actions.map((action, idx) => (
                          <Box key={idx} display="flex" gap={1} alignItems="flex-start">
                            <TimelineIcon color="secondary" sx={{ mt: 0.5, flexShrink: 0 }} />
                            <Typography variant="body2">{action}</Typography>
                          </Box>
                        ))}
                      </Stack>
                    </CardContent>
                  </Card>
                </Stack>
              ) : (
                <Box
                  height={260}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  sx={{ color: 'text.secondary' }}
                >
                  <Typography variant="body1">
                    Run orchestration to see multi-agent results.
                  </Typography>
                </Box>
              )}
            </Paper>
          </TabPanel>
        </Grid>

        {/* Articles Section - Only show in Quick Analysis tab */}
        {tabValue === 0 && analysis && (
          <Grid item xs={12}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    Key Insights
                  </Typography>
                  {analysis.summary.insights.length === 0 ? (
                    <Typography variant="body2" color="text.secondary">
                      No notable insights detected from the current batch of articles.
                    </Typography>
                  ) : (
                    <Stack spacing={1.5}>
                      {analysis.summary.insights.map((insight) => (
                        <Stack key={insight} direction="row" spacing={1} alignItems="center">
                          <InfoIcon color="primary" fontSize="small" />
                          <Typography variant="body2">{insight}</Typography>
                        </Stack>
                      ))}
                    </Stack>
                  )}
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    Recommended Next Steps
                  </Typography>
                  <Stack spacing={1.5}>
                    {analysis.summary.recommendations.map((recommendation) => (
                      <Stack key={recommendation} direction="row" spacing={1} alignItems="center">
                        <TrendingUpIcon color="secondary" fontSize="small" />
                        <Typography variant="body2">{recommendation}</Typography>
                      </Stack>
                    ))}
                  </Stack>
                </Paper>
              </Grid>
            </Grid>
          </Grid>
        )}

        {/* Articles Section */}
        {tabValue === 0 && analysis && (
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" mb={2}>
                <Typography variant="h6" fontWeight={600}>
                  Latest Articles
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {analysis.summary.top_keywords.map((keyword) => (
                    <Chip
                      key={keyword}
                      label={keyword}
                      size="small"
                      variant="outlined"
                      color="primary"
                    />
                  ))}
                </Stack>
              </Stack>

              <Stack spacing={2}>
                {analysis.articles.length === 0 && (
                  <Typography variant="body2" color="text.secondary">
                    No recent articles found for this brand. Try widening the timeframe.
                  </Typography>
                )}

                {analysis.articles.map((article) => (
                  <Paper key={article.url ?? article.title} variant="outlined" sx={{ p: 2 }}>
                    <Stack
                      direction={{ xs: 'column', md: 'row' }}
                      spacing={2}
                      alignItems={{ md: 'center' }}
                    >
                      <Stack spacing={1} flex={1}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {article.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {article.source || 'Unknown source'} •{' '}
                          {article.published_at
                            ? new Date(article.published_at).toLocaleString()
                            : 'Date unavailable'}
                        </Typography>
                        {article.excerpt && (
                          <Typography variant="body2" color="text.secondary">
                            {article.excerpt}
                          </Typography>
                        )}
                        <Stack direction="row" spacing={1} flexWrap="wrap">
                          {article.keywords.slice(0, 4).map((keyword) => (
                            <Chip key={keyword} label={keyword} size="small" />
                          ))}
                        </Stack>
                      </Stack>

                      <Stack spacing={1} alignItems={{ xs: 'flex-start', md: 'flex-end' }}>
                        <Chip
                          label={article.sentiment}
                          color={
                            article.sentiment === 'positive'
                              ? 'success'
                              : article.sentiment === 'negative'
                              ? 'error'
                              : 'info'
                          }
                        />
                        <Typography variant="body2" color="text.secondary">
                          Score: {article.sentiment_score.toFixed(2)}
                        </Typography>
                        {article.url && (
                          <Button
                            variant="text"
                            size="small"
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            endIcon={<LaunchIcon fontSize="small" />}
                          >
                            Read article
                          </Button>
                        )}
                      </Stack>
                    </Stack>
                  </Paper>
                ))}
              </Stack>
            </Paper>
          </Grid>
        )}

        {/* Orchestration Articles Section */}
        {tabValue === 1 && orchestration && (
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" mb={2}>
                <Typography variant="h6" fontWeight={600}>
                  Analyzed Articles ({orchestration.articles.length})
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {orchestration.summary.top_keywords.map((keyword) => (
                    <Chip
                      key={keyword}
                      label={keyword}
                      size="small"
                      variant="outlined"
                      color="primary"
                    />
                  ))}
                </Stack>
              </Stack>

              <Stack spacing={2}>
                {orchestration.articles.map((article) => (
                  <Paper key={article.url ?? article.title} variant="outlined" sx={{ p: 2 }}>
                    <Stack
                      direction={{ xs: 'column', md: 'row' }}
                      spacing={2}
                      alignItems={{ md: 'center' }}
                    >
                      <Stack spacing={1} flex={1}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {article.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {article.source || 'Unknown source'} •{' '}
                          {article.published_at
                            ? new Date(article.published_at).toLocaleString()
                            : 'Date unavailable'}
                        </Typography>
                        {article.excerpt && (
                          <Typography variant="body2" color="text.secondary">
                            {article.excerpt}
                          </Typography>
                        )}
                        <Stack direction="row" spacing={1} flexWrap="wrap">
                          {article.keywords.slice(0, 4).map((keyword) => (
                            <Chip key={keyword} label={keyword} size="small" />
                          ))}
                        </Stack>
                      </Stack>

                      <Stack spacing={1} alignItems={{ xs: 'flex-start', md: 'flex-end' }}>
                        <Chip
                          label={article.sentiment}
                          color={
                            article.sentiment === 'positive'
                              ? 'success'
                              : article.sentiment === 'negative'
                              ? 'error'
                              : 'info'
                          }
                        />
                        <Typography variant="body2" color="text.secondary">
                          Score: {article.sentiment_score.toFixed(2)}
                        </Typography>
                        {article.url && (
                          <Button
                            variant="text"
                            size="small"
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            endIcon={<LaunchIcon fontSize="small" />}
                          >
                            Read article
                          </Button>
                        )}
                      </Stack>
                    </Stack>
                  </Paper>
                ))}
              </Stack>
            </Paper>
          </Grid>
        )}

        {!analysis && !orchestration && !isLoading && (
          <Grid item xs={12}>
            <Paper elevation={0} sx={{ mt: 4, p: 3, bgcolor: '#ffffff' }}>
              <Stack direction="row" spacing={2} alignItems="center">
                <ArticleIcon color="primary" />
                <Box>
                  <Typography variant="subtitle1" fontWeight={600}>
                    Tip: Try multiple brands
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Start with your own brand, then compare with competitors to spot emerging trends.
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default Dashboard;
