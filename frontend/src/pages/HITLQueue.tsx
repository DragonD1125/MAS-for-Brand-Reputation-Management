import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

const HITLQueue: React.FC = () => {
  return (
    <Box p={4}>
      <Paper sx={{ p: 3 }} elevation={1}>
        <Typography variant="h5" fontWeight={600} gutterBottom>
          Human-in-the-Loop Queue Offline
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Automated response approval workflows are paused while social data sources are disabled. Continue using the
          NewsAPI-based dashboard to review brand coverage and take manual actions if needed.
        </Typography>
      </Paper>
    </Box>
  );
};

export default HITLQueue;
