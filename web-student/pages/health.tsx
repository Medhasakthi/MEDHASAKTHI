import React from 'react';

const HealthPage: React.FC = () => {
  return (
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '100vh',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ color: '#22c55e', marginBottom: '1rem' }}>✓ Healthy</h1>
        <p style={{ color: '#64748b' }}>MEDHASAKTHI Student Portal is running</p>
        <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
          {new Date().toISOString()}
        </p>
      </div>
    </div>
  );
};

export default HealthPage;
