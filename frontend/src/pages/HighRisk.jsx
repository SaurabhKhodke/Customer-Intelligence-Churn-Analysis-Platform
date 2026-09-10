import React, { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import { getHighRiskCustomers } from '../services/api';
import CustomerTable from '../components/CustomerTable';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const HighRisk = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch a larger chunk for the full page
        const data = await getHighRiskCustomers(200, 0);
        setCustomers(data.customers);
      } catch (err) {
        setError(err.message || 'Failed to load high risk customers.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle size={24} style={{ color: '#ef4444' }} />
        <div>
          <h1 style={{ fontSize: '1.5rem', margin: 0 }}>High Risk Customers</h1>
          <p className="text-muted" style={{ margin: 0, marginTop: '0.25rem' }}>Customers with highest predicted probability of churn.</p>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <LoadingSpinner />
        ) : error ? (
          <ErrorMessage message={error} />
        ) : (
          <CustomerTable customers={customers} />
        )}
      </div>
    </div>
  );
};

export default HighRisk;
