import React from 'react';

const StatCard = ({ title, value, subtitle, icon: Icon }) => {
  return (
    <div className="card">
      <div className="flex justify-between items-center mb-2">
        <h3 className="card-title text-muted" style={{ fontSize: '0.875rem' }}>{title}</h3>
        {Icon && <Icon size={18} className="text-muted" />}
      </div>
      <div style={{ fontSize: '1.8rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
        {value}
      </div>
      {subtitle && (
        <div className="text-muted" style={{ fontSize: '0.8rem' }}>
          {subtitle}
        </div>
      )}
    </div>
  );
};

export default StatCard;
