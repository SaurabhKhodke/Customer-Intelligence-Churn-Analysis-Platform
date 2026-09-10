import React from 'react';

const RiskBadge = ({ risk }) => {
  if (!risk) return null;
  
  const normalizedRisk = risk.toUpperCase();
  const badgeClass = `badge badge-${normalizedRisk.toLowerCase()}`;
  
  return (
    <span className={badgeClass}>
      {normalizedRisk}
    </span>
  );
};

export default RiskBadge;
