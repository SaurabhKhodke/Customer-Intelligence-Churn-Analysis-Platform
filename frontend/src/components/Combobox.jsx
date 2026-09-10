import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

const Combobox = ({ name, value, options, onChange, placeholder = "Select or type..." }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState(value || '');
  const [searchValue, setSearchValue] = useState('');
  const wrapperRef = useRef(null);

  // Sync external value changes (e.g. from preset buttons)
  useEffect(() => {
    setInputValue(value || '');
  }, [value]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
        // On blur, fire change with whatever text is there
        if (inputValue !== value) {
          onChange({ target: { name, value: inputValue } });
        }
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [wrapperRef, inputValue, value, name, onChange]);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    setSearchValue(e.target.value);
    setIsOpen(true);
    // Also update parent immediately so they can track custom input
    onChange({ target: { name, value: e.target.value } });
  };

  const handleOptionClick = (option) => {
    setInputValue(option);
    setSearchValue('');
    setIsOpen(false);
    onChange({ target: { name, value: option } });
  };

  const handleFocus = () => {
    setIsOpen(true);
    setSearchValue('');
  };

  const filteredOptions = options.filter(option => 
    option.toLowerCase().includes(searchValue.toLowerCase())
  );

  return (
    <div className="combobox-wrapper" ref={wrapperRef} style={{ position: 'relative', width: '100%' }}>
      <div className="flex items-center" style={{ position: 'relative' }}>
        <input
          type="text"
          className="form-control"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={handleFocus}
          placeholder={placeholder}
          style={{ width: '100%', paddingRight: '2rem' }}
          autoComplete="off"
        />
        <ChevronDown 
          size={16} 
          className="text-muted" 
          style={{ 
            position: 'absolute', 
            right: '0.75rem', 
            cursor: 'pointer',
            pointerEvents: 'none'
          }} 
        />
      </div>

      {isOpen && (
        <ul 
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            zIndex: 50,
            maxHeight: '200px',
            overflowY: 'auto',
            backgroundColor: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--border-radius)',
            marginTop: '0.25rem',
            padding: '0.25rem 0',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            listStyle: 'none'
          }}
        >
          {filteredOptions.length > 0 ? (
            filteredOptions.map((option, idx) => (
              <li 
                key={idx}
                onClick={() => handleOptionClick(option)}
                style={{
                  padding: '0.5rem 1rem',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  color: 'var(--text-primary)',
                  transition: 'background-color 0.15s ease'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = 'var(--bg-main)'}
                onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
              >
                {option}
              </li>
            ))
          ) : (
            <li style={{ padding: '0.5rem 1rem', fontSize: '0.875rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
              Press enter to use "{searchValue || inputValue}"
            </li>
          )}
        </ul>
      )}
    </div>
  );
};

export default Combobox;
