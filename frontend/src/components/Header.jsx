import React from 'react';
import { User, Bell, Search } from 'lucide-react';

const Header = ({ title }) => {
  return (
    <header className="top-header">
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</h2>
      </div>
      
      <div className="flex items-center gap-4">
        <div style={{ position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            placeholder="Search..." 
            className="form-control"
            style={{ paddingLeft: '2.25rem', width: '250px', borderRadius: '20px', height: '36px' }}
          />
        </div>
        
        <button className="btn btn-outline" style={{ padding: '0.4rem', border: 'none' }}>
          <Bell size={20} className="text-muted" />
        </button>
        
        <div className="flex items-center gap-2" style={{ borderLeft: '1px solid var(--border-color)', paddingLeft: '1rem' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--bg-main)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <User size={18} className="text-secondary" />
          </div>
          <div style={{ fontSize: '0.85rem' }}>
            <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Admin User</div>
            <div className="text-muted" style={{ fontSize: '0.75rem' }}>Data Science</div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
