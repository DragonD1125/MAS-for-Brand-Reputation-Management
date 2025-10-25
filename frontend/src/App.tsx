import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Mentions from './pages/Mentions';
import HITLQueue from './pages/HITLQueue';
import Analytics from './pages/Analytics';
import SystemHealth from './pages/SystemHealth';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Navbar />
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/mentions" element={<Mentions />} />
          <Route path="/hitl-queue" element={<HITLQueue />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/system-health" element={<SystemHealth />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default App;
