import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

const SystemHealth: React.FC = () => {
  return (
    <Box p={4}>
      <Paper sx={{ p: 3 }} elevation={1}>
        <Typography variant="h5" fontWeight={600} gutterBottom>
          System Health Overview
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Detailed infrastructure telemetry is disabled while the platform operates in NewsAPI-only mode. Monitor
          backend logs directly if you need runtime health details.
        </Typography>
      </Paper>
    </Box>
  );
};

export default SystemHealth;
