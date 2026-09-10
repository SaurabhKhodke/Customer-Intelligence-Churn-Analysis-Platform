import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import CustomerDetails from './pages/CustomerDetails';
import HighRisk from './pages/HighRisk';
import Prediction from './pages/Prediction';
import Analytics from './pages/Analytics';
import AIInsights from './pages/AIInsights';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="dashboard" element={<Navigate to="/" replace />} />
          <Route path="customers" element={<Customers />} />
          <Route path="customers/:customerId" element={<CustomerDetails />} />
          <Route path="high-risk" element={<HighRisk />} />
          <Route path="prediction" element={<Prediction />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="ai-insights" element={<AIInsights />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
