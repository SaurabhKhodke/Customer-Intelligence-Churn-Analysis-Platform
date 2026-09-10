import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

const Layout = () => {
  const location = useLocation();
  
  // Create a nice title based on the route
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/' || path === '/dashboard') return 'Dashboard';
    if (path === '/customers') return 'Customers';
    if (path.startsWith('/customers/')) return 'Customer Details';
    if (path === '/high-risk') return 'High Risk Customers';
    if (path === '/prediction') return 'Churn Prediction';
    if (path === '/analytics') return 'Analytics';
    if (path === '/ai-insights') return 'AI Insights';
    return 'Customer Intelligence';
  };

  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        <Header title={getPageTitle()} />
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
