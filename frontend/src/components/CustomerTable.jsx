import React from 'react';
import { useNavigate } from 'react-router-dom';
import RiskBadge from './RiskBadge';

const CustomerTable = ({ customers }) => {
  const navigate = useNavigate();

  if (!customers || customers.length === 0) {
    return <div className="text-muted p-4 text-center">No customers found.</div>;
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Customer ID</th>
            <th>Churn Prob.</th>
            <th>Risk</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {customers.map((c) => (
            <tr key={c.customer_id}>
              <td style={{ fontWeight: 500 }}>{c.customer_id}</td>
              <td>{(c.churn_probability * 100).toFixed(1)}%</td>
              <td><RiskBadge risk={c.risk} /></td>
              <td>
                <button 
                  className="btn btn-outline" 
                  style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                  onClick={() => navigate(`/customers/${c.customer_id}`)}
                >
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CustomerTable;
