import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  InputAdornment,
  Chip,
  Card,
  CardContent,
  Avatar,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Visibility as ViewIcon,
  ThumbUp,
  ThumbDown,
  Share,
  MoreVert,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { mentionsApi } from '../services/api';
import InfiniteScroll from 'react-infinite-scroll-component';
import moment from 'moment';

interface Mention {
  id: string;
  content: string;
  author: string;
  platform: string;
  timestamp: string;
  sentiment_score: number;
  sentiment_label: string;
  crisis_flag: boolean;
  engagement_metrics: {
    likes: number;
    shares: number;
    comments: number;
  };
  ai_analysis?: any;
}

const Mentions: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMention, setSelectedMention] = useState<Mention | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [mentions, setMentions] = useState<Mention[]>([]);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['mentions', searchTerm, page],
    queryFn: () => mentionsApi.getMentions({ 
      search: searchTerm,
      page: page,
      limit: 20 
    }).then(res => {
      if (page === 1) {
        setMentions(res.data.items || []);
      } else {
        setMentions(prev => [...prev, ...(res.data.items || [])]);
      }
      return res.data;
    }),
    enabled: true,
  });

  const handleViewDetails = async (mention: Mention) => {
    try {
      const response = await mentionsApi.getMentionById(mention.id);
      setSelectedMention(response.data);
      setDialogOpen(true);
    } catch (error) {
      console.error('Failed to fetch mention details:', error);
    }
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.1) return 'success';
    if (score < -0.1) return 'error';
    return 'warning';
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      case 'neutral': return '😐';
      default: return '🤔';
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'twitter': return '🐦';
      case 'facebook': return '👤';
      case 'instagram': return '📷';
      case 'reddit': return '🤖';
      default: return '💬';
    }
  };

  const loadMore = () => {
    setPage(prev => prev + 1);
  };

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load mentions. Please check your connection.
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Brand Mentions Feed
        </Typography>
        <Box display="flex" gap={2}>
          <TextField
            placeholder="Search mentions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ width: 300 }}
          />
          <Button startIcon={<FilterIcon />} variant="outlined">
            Filters
          </Button>
        </Box>
      </Box>

      {isLoading && mentions.length === 0 ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <InfiniteScroll
          dataLength={mentions.length}
          next={loadMore}
          hasMore={data?.has_more || false}
          loader={
            <Box display="flex" justifyContent="center" p={2}>
              <CircularProgress size={24} />
            </Box>
          }
          endMessage={
            <Typography align="center" color="textSecondary" p={2}>
              No more mentions to load
            </Typography>
          }
        >
          <Grid container spacing={2}>
            {mentions.map((mention) => (
              <Grid item xs={12} key={mention.id}>
                <Card sx={{ bgcolor: 'background.paper', border: mention.crisis_flag ? '2px solid red' : 'none' }}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                      <Box display="flex" gap={2} flexGrow={1}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          {getPlatformIcon(mention.platform)}
                        </Avatar>
                        <Box flexGrow={1}>
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            <Typography variant="h6">@{mention.author}</Typography>
                            <Chip
                              label={mention.platform}
                              size="small"
                              variant="outlined"
                            />
                            <Chip
                              label={`${getSentimentIcon(mention.sentiment_label)} ${mention.sentiment_label}`}
                              size="small"
                              color={getSentimentColor(mention.sentiment_score)}
                            />
                            {mention.crisis_flag && (
                              <Chip
                                label="CRISIS"
                                size="small"
                                color="error"
                                variant="filled"
                              />
                            )}
                          </Box>
                          <Typography variant="body1" mb={2}>
                            {mention.content}
                          </Typography>
                          <Box display="flex" alignItems="center" gap={3}>
                            <Box display="flex" alignItems="center" gap={1}>
                              <ThumbUp fontSize="small" />
                              <Typography variant="caption">
                                {mention.engagement_metrics?.likes || 0}
                              </Typography>
                            </Box>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Share fontSize="small" />
                              <Typography variant="caption">
                                {mention.engagement_metrics?.shares || 0}
                              </Typography>
                            </Box>
                            <Typography variant="caption" color="textSecondary">
                              {moment(mention.timestamp).fromNow()}
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                      <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
                        <IconButton
                          onClick={() => handleViewDetails(mention)}
                          color="primary"
                        >
                          <ViewIcon />
                        </IconButton>
                        <IconButton>
                          <MoreVert />
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </InfiniteScroll>
      )}

      {/* Mention Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="h6">
              Mention Details & AI Analysis
            </Typography>
            {selectedMention?.crisis_flag && (
              <Chip label="CRISIS" color="error" />
            )}
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedMention && (
            <Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Content
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Typography>{selectedMention.content}</Typography>
                  </Paper>
                  
                  <Box mt={2}>
                    <Typography variant="h6" gutterBottom>
                      Metadata
                    </Typography>
                    <Box display="flex" flexDirection="column" gap={1}>
                      <Typography variant="body2">
                        <strong>Author:</strong> @{selectedMention.author}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Platform:</strong> {selectedMention.platform}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Posted:</strong> {moment(selectedMention.timestamp).format('LLLL')}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Sentiment Score:</strong> {selectedMention.sentiment_score?.toFixed(3)}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    AI Analysis
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'background.default', maxHeight: 400, overflow: 'auto' }}>
                    {selectedMention.ai_analysis ? (
                      <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                        {JSON.stringify(selectedMention.ai_analysis, null, 2)}
                      </pre>
                    ) : (
                      <Typography color="textSecondary">
                        No AI analysis available for this mention.
                      </Typography>
                    )}
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Mentions;
