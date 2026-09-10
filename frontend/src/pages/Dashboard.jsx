import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Users, AlertCircle, Percent, TrendingUp } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getDashboardSummary, getRiskSummary, getHighRiskCustomers } from '../services/api';
import StatCard from '../components/StatCard';
import CustomerTable from '../components/CustomerTable';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [riskData, setRiskData] = useState(null);
  const [highRiskPreview, setHighRiskPreview] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [dash, risk, highRisk] = await Promise.all([
          getDashboardSummary(),
          getRiskSummary(),
          getHighRiskCustomers(5, 0)
        ]);
        setDashboardData(dash);
        
        // Format for Recharts
        const chartData = [
          { name: 'HIGH', value: risk.risk_distribution.HIGH || 0, color: '#fca5a5' },
          { name: 'MEDIUM', value: risk.risk_distribution.MEDIUM || 0, color: '#fcd34d' },
          { name: 'LOW', value: risk.risk_distribution.LOW || 0, color: '#86efac' }
        ];
        setRiskData(chartData);
        setHighRiskPreview(highRisk.customers);
      } catch (err) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!dashboardData) return null;

  return (
    <div>
      <div className="mb-4">
        <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Overview of customer churn and risk</h1>
        <p className="text-muted">High-level business metrics and risk distribution.</p>
      </div>

      <div className="grid-cols-4 mb-4">
        <StatCard 
          title="Total Customers" 
          value={dashboardData.total_customers.toLocaleString()} 
          icon={Users} 
        />
        <StatCard 
          title="Predicted Churn" 
          value={dashboardData.predicted_churn_customers.toLocaleString()} 
          icon={TrendingUp} 
        />
        <StatCard 
          title="Avg Churn Probability" 
          value={`${(dashboardData.average_churn_probability * 100).toFixed(1)}%`} 
          icon={Percent} 
        />
        <StatCard 
          title="High Risk Customers" 
          value={dashboardData.high_risk_customers.toLocaleString()} 
          icon={AlertCircle} 
        />
      </div>

      <div className="grid-cols-2 mb-4">
        <div className="card" style={{ height: '350px' }}>
          <h3 className="card-title mb-3">Risk Distribution</h3>
          {riskData && (
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => value.toLocaleString()} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
        
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', backgroundColor: 'var(--bg-main)', border: 'none' }}>
           <div style={{ textAlign: 'center', maxWidth: '300px' }}>
             <AlertCircle size={48} style={{ color: 'var(--primary)', margin: '0 auto 1rem auto' }} />
             <h3 style={{ marginBottom: '0.5rem' }}>Need deeper insights?</h3>
             <p className="text-muted mb-3">Use the AI Insights tool to query customer behavior and churn drivers.</p>
             <Link to="/ai-insights" className="btn btn-primary">Go to AI Insights</Link>
           </div>
        </div>
      </div>

      <div className="card">
        <div className="flex justify-between items-center mb-3">
          <h3 className="card-title">Recent High Risk Customers</h3>
          <Link to="/high-risk" className="btn btn-outline" style={{ fontSize: '0.8rem' }}>View All</Link>
        </div>
        <CustomerTable customers={highRiskPreview} />
      </div>
    </div>
  );
};

export default Dashboard;
