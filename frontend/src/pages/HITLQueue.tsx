import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Alert,
  CircularProgress,
  IconButton,
  Badge,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Visibility,
  PriorityHigh,
  Schedule,
  Person,
  AutoMode,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { hitlApi } from '../services/api';
import moment from 'moment';
import { toast } from 'react-toastify';

interface HITLItem {
  id: string;
  type: 'response_approval' | 'crisis_escalation' | 'content_review';
  priority: 'low' | 'medium' | 'high' | 'critical';
  created_at: string;
  expires_at: string;
  content: {
    original_mention: any;
    proposed_response: string;
    ai_reasoning: string;
    confidence_score: number;
    risk_assessment: string;
  };
  status: 'pending' | 'approved' | 'rejected';
  assigned_to?: string;
}

const HITLQueue: React.FC = () => {
  const [selectedItem, setSelectedItem] = useState<HITLItem | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [feedback, setFeedback] = useState('');
  const queryClient = useQueryClient();

  const { data: queueItems, isLoading, error } = useQuery({
    queryKey: ['hitl-queue'],
    queryFn: () => hitlApi.getQueue().then(res => res.data),
    refetchInterval: 10000, // Refetch every 10 seconds for real-time updates
  });

  const approveMutation = useMutation({
    mutationFn: (data: { id: string; feedback: string }) =>
      hitlApi.approveResponse(data.id, { feedback: data.feedback }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hitl-queue'] });
      toast.success('Response approved successfully');
      setDetailsOpen(false);
      setFeedback('');
    },
    onError: () => toast.error('Failed to approve response'),
  });

  const rejectMutation = useMutation({
    mutationFn: (data: { id: string; feedback: string }) =>
      hitlApi.rejectResponse(data.id, { feedback: data.feedback }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hitl-queue'] });
      toast.success('Response rejected');
      setDetailsOpen(false);
      setFeedback('');
    },
    onError: () => toast.error('Failed to reject response'),
  });

  const handleApprove = () => {
    if (selectedItem) {
      approveMutation.mutate({ id: selectedItem.id, feedback });
    }
  };

  const handleReject = () => {
    if (selectedItem) {
      rejectMutation.mutate({ id: selectedItem.id, feedback });
    }
  };

  const handleViewDetails = async (item: HITLItem) => {
    try {
      const response = await hitlApi.getResponseById(item.id);
      setSelectedItem(response.data);
      setDetailsOpen(true);
    } catch (error) {
      console.error('Failed to fetch item details:', error);
      setSelectedItem(item);
      setDetailsOpen(true);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'response_approval': return <AutoMode />;
      case 'crisis_escalation': return <PriorityHigh />;
      case 'content_review': return <Visibility />;
      default: return <Schedule />;
    }
  };

  const isExpiringSoon = (expiresAt: string) => {
    const now = moment();
    const expires = moment(expiresAt);
    return expires.diff(now, 'minutes') < 30;
  };

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load HITL queue. Please check your connection.
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Human-in-the-Loop Queue
        </Typography>
        <Box display="flex" gap={2}>
          <Badge badgeContent={queueItems?.filter((item: HITLItem) => item.priority === 'critical').length || 0} color="error">
            <Chip label="Critical" color="error" />
          </Badge>
          <Badge badgeContent={queueItems?.filter((item: HITLItem) => item.priority === 'high').length || 0} color="warning">
            <Chip label="High Priority" color="warning" />
          </Badge>
          <Badge badgeContent={queueItems?.length || 0} color="primary">
            <Chip label="Total Pending" color="primary" />
          </Badge>
        </Box>
      </Box>

      {isLoading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {queueItems?.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                All caught up!
              </Typography>
              <Typography color="textSecondary">
                No pending items in the Human-in-the-Loop queue. The AI system is operating autonomously.
              </Typography>
            </Paper>
          ) : (
            <Grid container spacing={3}>
              {queueItems?.map((item: HITLItem) => (
                <Grid item xs={12} md={6} lg={4} key={item.id}>
                  <Card
                    sx={{
                      height: '100%',
                      border: item.priority === 'critical' ? '2px solid red' : 
                             isExpiringSoon(item.expires_at) ? '2px solid orange' : 'none',
                      position: 'relative',
                    }}
                  >
                    {isExpiringSoon(item.expires_at) && (
                      <Box
                        sx={{
                          position: 'absolute',
                          top: 0,
                          right: 0,
                          bgcolor: 'warning.main',
                          color: 'white',
                          px: 1,
                          py: 0.5,
                          fontSize: '0.75rem',
                          borderBottomLeftRadius: 4,
                        }}
                      >
                        EXPIRES SOON
                      </Box>
                    )}
                    
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={1} mb={2}>
                        {getTypeIcon(item.type)}
                        <Typography variant="h6" noWrap>
                          {item.type.replace('_', ' ').toUpperCase()}
                        </Typography>
                        <Chip
                          label={item.priority}
                          color={getPriorityColor(item.priority)}
                          size="small"
                        />
                      </Box>

                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Confidence: {(item.content.confidence_score * 100).toFixed(1)}%
                      </Typography>

                      <Typography variant="body1" sx={{ 
                        mb: 2,
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}>
                        {item.content.proposed_response}
                      </Typography>

                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="caption" color="textSecondary">
                          Created: {moment(item.created_at).fromNow()}
                        </Typography>
                        <Typography variant="caption" color="error">
                          Expires: {moment(item.expires_at).fromNow()}
                        </Typography>
                      </Box>

                      {item.assigned_to && (
                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                          <Person fontSize="small" />
                          <Typography variant="caption">
                            Assigned to: {item.assigned_to}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>

                    <CardActions sx={{ justifyContent: 'space-between', p: 2 }}>
                      <Button
                        size="small"
                        onClick={() => handleViewDetails(item)}
                        startIcon={<Visibility />}
                      >
                        Details
                      </Button>
                      <Box display="flex" gap={1}>
                        <Button
                          size="small"
                          color="error"
                          onClick={() => {
                            setSelectedItem(item);
                            setDetailsOpen(true);
                          }}
                          startIcon={<Cancel />}
                        >
                          Reject
                        </Button>
                        <Button
                          size="small"
                          color="success"
                          variant="contained"
                          onClick={() => {
                            setSelectedItem(item);
                            setDetailsOpen(true);
                          }}
                          startIcon={<CheckCircle />}
                        >
                          Approve
                        </Button>
                      </Box>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </>
      )}

      {/* Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="h6">
              HITL Review - {selectedItem?.type.replace('_', ' ').toUpperCase()}
            </Typography>
            {selectedItem && (
              <Chip
                label={selectedItem.priority}
                color={getPriorityColor(selectedItem.priority)}
              />
            )}
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Original Mention
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'background.default', mb: 2 }}>
                    <Typography>{selectedItem.content.original_mention?.content || 'N/A'}</Typography>
                  </Paper>

                  <Typography variant="h6" gutterBottom>
                    Proposed Response
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'background.default', mb: 2 }}>
                    <Typography>{selectedItem.content.proposed_response}</Typography>
                  </Paper>

                  <Typography variant="h6" gutterBottom>
                    AI Reasoning
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'background.default', mb: 2 }}>
                    <Typography>{selectedItem.content.ai_reasoning}</Typography>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Risk Assessment
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'background.default', mb: 2 }}>
                    <Typography>{selectedItem.content.risk_assessment}</Typography>
                  </Paper>

                  <Typography variant="h6" gutterBottom>
                    Confidence Score
                  </Typography>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <CircularProgress
                      variant="determinate"
                      value={selectedItem.content.confidence_score * 100}
                      size={60}
                    />
                    <Typography variant="h4">
                      {(selectedItem.content.confidence_score * 100).toFixed(1)}%
                    </Typography>
                  </Box>

                  <Typography variant="h6" gutterBottom>
                    Your Feedback
                  </Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    placeholder="Provide feedback for the AI system to learn from..."
                    sx={{ mb: 2 }}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setDetailsOpen(false)}>Cancel</Button>
          <Button
            onClick={handleReject}
            color="error"
            disabled={rejectMutation.isPending}
            startIcon={<Cancel />}
          >
            {rejectMutation.isPending ? 'Rejecting...' : 'Reject'}
          </Button>
          <Button
            onClick={handleApprove}
            color="success"
            variant="contained"
            disabled={approveMutation.isPending}
            startIcon={<CheckCircle />}
          >
            {approveMutation.isPending ? 'Approving...' : 'Approve & Deploy'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HITLQueue;
