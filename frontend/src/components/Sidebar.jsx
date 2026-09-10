import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, AlertTriangle, Calculator, BarChart2, BrainCircuit } from 'lucide-react';
import { getHealth } from '../services/api';

const Sidebar = () => {
  const [health, setHealth] = useState({ status: 'checking', connected: false });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await getHealth();
        setHealth({ status: data.status, connected: true });
      } catch (err) {
        setHealth({ status: 'error', connected: false });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/customers', label: 'Customers', icon: Users },
    { path: '/high-risk', label: 'High Risk', icon: AlertTriangle },
    { path: '/prediction', label: 'Prediction', icon: Calculator },
    { path: '/analytics', label: 'Analytics', icon: BarChart2 },
    { path: '/ai-insights', label: 'AI Insights', icon: BrainCircuit },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-title">Customer Intelligence</div>
      </div>
      
      <div className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <item.icon size={18} />
            {item.label}
          </NavLink>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="flex items-center">
          <span className={`status-indicator ${health.connected ? 'connected' : 'error'}`}></span>
          <span>API Status: {health.connected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
