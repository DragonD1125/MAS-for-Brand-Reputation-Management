import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

const Mentions: React.FC = () => {
  return (
    <Box p={4}>
      <Paper sx={{ p: 3 }} elevation={1}>
        <Typography variant="h5" fontWeight={600} gutterBottom>
          Mentions Feed Unavailable
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Social platform integrations (Twitter, Reddit, Instagram) are disabled in this environment. The NewsAPI
          workflow on the main dashboard provides the most up-to-date coverage for your brand.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Mentions;
