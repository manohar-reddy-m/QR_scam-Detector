import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { SecurityOverview } from './pages/SecurityOverview';
import { QRAnalysis } from './pages/QRAnalysis';
import { ThreatAssessment } from './pages/ThreatAssessment';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30000,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<SecurityOverview />} />
            <Route path="analyze" element={<QRAnalysis />} />
            <Route path="qr" element={<Navigate to="/analyze" replace />} />
            <Route path="url" element={<ThreatAssessment />} />
            <Route path="threat" element={<Navigate to="/url" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
