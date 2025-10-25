import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Alert,
  Chip,
  LinearProgress,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Info,
  Refresh,
  Storage,
  Memory,
  Speed,
  NetworkCheck,
  SmartToy,
  Psychology,
  Timeline,
  Settings,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { monitoringApi } from '../services/api';
import moment from 'moment';

interface SystemStatus {
  status: 'healthy' | 'warning' | 'error';
  uptime: number;
  memory_usage_percent: number;
  cpu_usage_percent: number;
  disk_usage_percent: number;
  response_time_ms: number;
  active_agents: number;
  database_status: string;
  redis_status: string;
  last_error?: string;
}

interface AgentStatus {
  name: string;
  status: 'active' | 'idle' | 'error';
  last_action: string;
  processed_today: number;
  error_rate: number;
}

const SystemHealth: React.FC = () => {
  const [logsOpen, setLogsOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  const { data: systemStatus, isLoading: statusLoading, refetch: refetchStatus } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => monitoringApi.getSystemHealth().then(res => res.data),
    refetchInterval: 5000, // Very frequent updates for system health
  });

  const { data: performance, isLoading: perfLoading } = useQuery({
    queryKey: ['performance'],
    queryFn: () => monitoringApi.getPerformance().then(res => res.data),
    refetchInterval: 10000,
  });

  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ['system-alerts'],
    queryFn: () => monitoringApi.getAlerts().then(res => res.data),
    refetchInterval: 15000,
  });

  // Mock agent statuses for demonstration
  const agentStatuses: AgentStatus[] = [
    {
      name: 'Data Collection Agent',
      status: 'active',
      last_action: 'Collected 23 new mentions',
      processed_today: 1247,
      error_rate: 0.02,
    },
    {
      name: 'Sentiment Analysis Agent',
      status: 'active',
      last_action: 'Analyzed sentiment for 18 mentions',
      processed_today: 1198,
      error_rate: 0.01,
    },
    {
      name: 'Alert Management Agent',
      status: 'idle',
      last_action: 'Checked for crisis indicators',
      processed_today: 87,
      error_rate: 0,
    },
    {
      name: 'Response Generation Agent',
      status: 'active',
      last_action: 'Generated response for escalation',
      processed_today: 45,
      error_rate: 0.05,
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'active':
        return 'success';
      case 'warning':
      case 'idle':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'active':
        return <CheckCircle color="success" />;
      case 'warning':
      case 'idle':
        return <Warning color="warning" />;
      case 'error':
        return <Error color="error" />;
      default:
        return <Info color="info" />;
    }
  };

  const MetricCard = ({ title, value, unit, icon, status, description }: any) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
          {icon}
        </Box>
        <Box display="flex" alignItems="baseline" gap={1} mb={1}>
          <Typography variant="h4" color={getStatusColor(status)}>
            {statusLoading ? <CircularProgress size={24} /> : value}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {unit}
          </Typography>
        </Box>
        <Typography variant="body2" color="textSecondary">
          {description}
        </Typography>
        {typeof value === 'number' && value > 0 && (
          <LinearProgress
            variant="determinate"
            value={Math.min(value, 100)}
            color={getStatusColor(status)}
            sx={{ mt: 1 }}
          />
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          System Health & Performance
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            startIcon={<Refresh />}
            onClick={() => refetchStatus()}
            variant="outlined"
          >
            Refresh
          </Button>
          <Chip
            label={systemStatus?.status?.toUpperCase() || 'UNKNOWN'}
            color={getStatusColor(systemStatus?.status || 'info')}
            icon={getStatusIcon(systemStatus?.status || 'info')}
          />
        </Box>
      </Box>

      {/* System Overview */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Uptime"
            value={systemStatus ? Math.floor(systemStatus.uptime / 3600) : 0}
            unit="hours"
            icon={<Timeline />}
            status="healthy"
            description="System running since startup"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Memory Usage"
            value={systemStatus?.memory_usage_percent || 0}
            unit="%"
            icon={<Memory />}
            status={systemStatus?.memory_usage_percent > 80 ? 'error' : 'healthy'}
            description="RAM utilization"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Response Time"
            value={systemStatus?.response_time_ms || 0}
            unit="ms"
            icon={<Speed />}
            status={systemStatus?.response_time_ms > 1000 ? 'warning' : 'healthy'}
            description="Average API response time"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Agents"
            value={systemStatus?.active_agents || 0}
            unit=""
            icon={<SmartToy />}
            status="healthy"
            description="AI agents running"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* System Alerts */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 400, overflow: 'auto' }}>
            <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
              <Typography variant="h6">System Alerts</Typography>
              <IconButton size="small">
                <Settings />
              </IconButton>
            </Box>
            
            {alertsLoading ? (
              <Box display="flex" justifyContent="center" p={2}>
                <CircularProgress />
              </Box>
            ) : alerts?.length > 0 ? (
              <List>
                {alerts.slice(0, 10).map((alert: any, index: number) => (
                  <ListItem key={index} divider>
                    <ListItemIcon>
                      {getStatusIcon(alert.severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={alert.message}
                      secondary={moment(alert.timestamp).fromNow()}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Alert severity="success">
                No active system alerts. All systems operating normally.
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Agent Status */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 400, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              AI Agent Status
            </Typography>
            
            <List>
              {agentStatuses.map((agent, index) => (
                <ListItem
                  key={index}
                  divider
                  sx={{
                    cursor: 'pointer',
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                  onClick={() => setSelectedAgent(agent.name)}
                >
                  <ListItemIcon>
                    <Psychology color={getStatusColor(agent.status)} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body1">{agent.name}</Typography>
                        <Chip
                          label={agent.status}
                          color={getStatusColor(agent.status)}
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          Last: {agent.last_action}
                        </Typography>
                        <Typography variant="caption" display="block">
                          Today: {agent.processed_today} processed, {(agent.error_rate * 100).toFixed(1)}% error rate
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Infrastructure Status */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Infrastructure Status
            </Typography>
            
            <Box display="flex" flexDirection="column" gap={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box display="flex" alignItems="center" gap={1}>
                  <Storage />
                  <Typography>Database</Typography>
                </Box>
                <Chip
                  label={systemStatus?.database_status || 'Unknown'}
                  color={systemStatus?.database_status === 'healthy' ? 'success' : 'error'}
                  size="small"
                />
              </Box>
              
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box display="flex" alignItems="center" gap={1}>
                  <NetworkCheck />
                  <Typography>Redis Cache</Typography>
                </Box>
                <Chip
                  label={systemStatus?.redis_status || 'Unknown'}
                  color={systemStatus?.redis_status === 'connected' ? 'success' : 'error'}
                  size="small"
                />
              </Box>
              
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box display="flex" alignItems="center" gap={1}>
                  <Storage />
                  <Typography>Disk Usage</Typography>
                </Box>
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="body2">
                    {systemStatus?.disk_usage_percent || 0}%
                  </Typography>
                  <CircularProgress
                    variant="determinate"
                    value={systemStatus?.disk_usage_percent || 0}
                    size={20}
                    color={systemStatus?.disk_usage_percent > 90 ? 'error' : 'success'}
                  />
                </Box>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Performance Metrics
            </Typography>
            
            {perfLoading ? (
              <Box display="flex" justifyContent="center" p={2}>
                <CircularProgress />
              </Box>
            ) : (
              <Box display="flex" flexDirection="column" gap={2}>
                <Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2">Requests/Second</Typography>
                    <Typography variant="h6" color="primary">
                      {performance?.requests_per_second || 0}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min((performance?.requests_per_second || 0) * 2, 100)}
                    color="primary"
                  />
                </Box>
                
                <Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2">Success Rate</Typography>
                    <Typography variant="h6" color="success.main">
                      {((performance?.success_rate || 0) * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(performance?.success_rate || 0) * 100}
                    color="success"
                  />
                </Box>
                
                <Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2">Queue Length</Typography>
                    <Typography variant="h6">
                      {performance?.queue_length || 0}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min((performance?.queue_length || 0) * 10, 100)}
                    color={performance?.queue_length > 10 ? 'warning' : 'info'}
                  />
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Agent Details Dialog */}
      <Dialog
        open={Boolean(selectedAgent)}
        onClose={() => setSelectedAgent(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Agent Details - {selectedAgent}
        </DialogTitle>
        <DialogContent>
          <Typography>
            Detailed agent information and logs would appear here.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedAgent(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SystemHealth;
