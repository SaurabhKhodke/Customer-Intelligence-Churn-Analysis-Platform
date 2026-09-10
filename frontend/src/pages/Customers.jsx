import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { getCustomer } from '../services/api';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';

const Customers = () => {
  const [searchId, setSearchId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchId.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      // Just test if it exists
      await getCustomer(searchId);
      navigate(`/customers/${searchId}`);
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setError('Customer not found. Please check the ID and try again.');
      } else {
        setError(err.message || 'An error occurred while searching.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', marginTop: '2rem' }}>
      <div className="card">
        <h2 className="card-title mb-2">Customer Lookup</h2>
        <p className="text-muted mb-4">Enter a Customer ID to view their detailed profile, churn risk, and behavior analysis.</p>
        
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="number"
            className="form-control"
            placeholder="e.g. 1, 42, 105"
            value={searchId}
            onChange={(e) => setSearchId(e.target.value)}
            disabled={loading}
            style={{ flexGrow: 1 }}
          />
          <button type="submit" className="btn btn-primary" disabled={loading || !searchId}>
            <Search size={18} />
            Search
          </button>
        </form>

        {loading && <LoadingSpinner text="Searching..." />}
        {error && <ErrorMessage message={error} />}
        
        <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--border-radius)', fontSize: '0.85rem' }}>
          <strong>Tip:</strong> You can find valid customer IDs in the High Risk table or Dashboard preview.
        </div>
      </div>
    </div>
  );
};

export default Customers;
