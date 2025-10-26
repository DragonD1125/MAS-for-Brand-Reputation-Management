import React from 'react';
import { AppBar, Toolbar, Typography, Box, Chip } from '@mui/material';
import NewspaperIcon from '@mui/icons-material/Newspaper';
import InsightsIcon from '@mui/icons-material/Insights';

const Navbar: React.FC = () => {
  return (
    <AppBar position="static" color="primary" elevation={0}>
      <Toolbar sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', py: 1 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          <Typography variant="h6" sx={{ fontWeight: 600, letterSpacing: 0.2 }}>
            Brand Reputation AI
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            Focused on real-time NewsAPI monitoring
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Chip
            icon={<NewspaperIcon fontSize="small" />}
            label="News Watch"
            sx={{ bgcolor: '#ffffff20', color: 'white', fontWeight: 500 }}
          />
          <Chip
            icon={<InsightsIcon fontSize="small" />}
            label="Sentiment Insights"
            variant="outlined"
            sx={{ borderColor: '#ffffff70', color: 'white' }}
          />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
