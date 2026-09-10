import React from 'react';
import { AlertCircle } from 'lucide-react';

const ErrorMessage = ({ message, title = "Error Loading Data" }) => {
  return (
    <div style={{
      backgroundColor: '#fef2f2',
      border: '1px solid #fca5a5',
      borderRadius: 'var(--border-radius)',
      padding: '1rem',
      color: '#991b1b',
      display: 'flex',
      gap: '0.75rem',
      alignItems: 'flex-start',
      margin: '1rem 0'
    }}>
      <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
      <div>
        <h4 style={{ margin: '0 0 0.25rem 0', fontWeight: 600 }}>{title}</h4>
        <p style={{ margin: 0, fontSize: '0.9rem' }}>{message}</p>
      </div>
    </div>
  );
};

export default ErrorMessage;
