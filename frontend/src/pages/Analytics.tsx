import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

const Analytics: React.FC = () => {
  return (
    <Box p={4}>
      <Paper sx={{ p: 3 }} elevation={1}>
        <Typography variant="h5" fontWeight={600} gutterBottom>
          Analytics Dashboard Simplified
        </Typography>
        <Typography variant="body1" color="text.secondary">
          The analytics experience is now consolidated into the primary dashboard. Use the "Run Brand Analysis"
          panel to generate real-time NewsAPI insights, sentiment breakdowns, and recommended actions for any brand.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Analytics;
