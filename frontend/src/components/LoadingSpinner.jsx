import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ text = "Loading data..." }) => {
  return (
    <div className="flex items-center justify-center" style={{ padding: '3rem', flexDirection: 'column', gap: '1rem', color: 'var(--text-muted)' }}>
      <Loader2 size={32} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
      <div>{text}</div>
    </div>
  );
};

export default LoadingSpinner;
