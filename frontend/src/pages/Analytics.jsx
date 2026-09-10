import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts';
import { getRiskSummary } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const Analytics = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const riskSummary = await getRiskSummary();
        
        // Format for Recharts
        const formattedData = [
          {
            name: 'Low Risk',
            count: riskSummary.risk_distribution.LOW || 0,
            fill: '#86efac'
          },
          {
            name: 'Medium Risk',
            count: riskSummary.risk_distribution.MEDIUM || 0,
            fill: '#fcd34d'
          },
          {
            name: 'High Risk',
            count: riskSummary.risk_distribution.HIGH || 0,
            fill: '#fca5a5'
          }
        ];
        
        setData({
          chartData: formattedData,
          total: riskSummary.total_customers
        });
      } catch (err) {
        setError(err.message || 'Failed to load analytics data.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!data) return null;

  return (
    <div>
      <div className="mb-4">
        <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Customer Analytics</h1>
        <p className="text-muted">Business intelligence and risk distribution analysis.</p>
      </div>

      <div className="card" style={{ height: '500px' }}>
        <h3 className="card-title mb-4">Risk Distribution Chart</h3>
        <ResponsiveContainer width="100%" height="90%">
          <BarChart
            data={data.chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
            <XAxis dataKey="name" axisLine={false} tickLine={false} />
            <YAxis axisLine={false} tickLine={false} />
            <RechartsTooltip cursor={{ fill: 'transparent' }} />
            <Legend />
            <Bar dataKey="count" name="Number of Customers" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="card bg-main">
        <h3 className="card-title text-muted" style={{ fontSize: '1rem' }}>Data Availability</h3>
        <p className="text-muted" style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
          Additional charts will be added as new analytics endpoints become available in the backend API.
        </p>
      </div>
    </div>
  );
};

export default Analytics;
