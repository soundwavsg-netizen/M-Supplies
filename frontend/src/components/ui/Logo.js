import React from 'react';
import { Link } from 'react-router-dom';

const Logo = ({ 
  variant = 'primary', // 'primary' or 'white'
  size = 'medium', // 'small', 'medium', 'large'
  className = '',
  linkTo = '/',
  showText = true 
}) => {
  const sizes = {
    small: 'h-8',
    medium: 'h-12',
    large: 'h-16'
  };

  const logoSrc = variant === 'white' 
    ? '/assets/m-supplies-logo-white.png'
    : '/assets/m-supplies-logo-transparent.png';

  const logoContent = (
    <div className={`flex items-center space-x-2 ${className}`}>
      <img
        src={logoSrc}
        alt="M Supplies"
        className={`${sizes[size]} w-auto`}
        onError={(e) => {
          // Fallback to text if image fails to load
          e.target.style.display = 'none';
          e.target.nextSibling.style.display = 'block';
        }}
      />
      {/* Fallback text logo (hidden by default, shown if image fails) */}
      <span 
        className={`text-xl font-bold ${variant === 'white' ? 'text-white' : 'text-slate-900'} hidden`}
        style={{ display: 'none' }}
      >
        M Supplies
      </span>
      {showText && (
        <span className={`text-lg font-semibold ${variant === 'white' ? 'text-white' : 'text-slate-900'} ml-2`}>
          M Supplies
        </span>
      )}
    </div>
  );

  // If linkTo is provided, wrap in Link
  if (linkTo) {
    return (
      <Link 
        to={linkTo} 
        className="flex items-center hover:opacity-80 transition-opacity"
        data-testid="logo-link"
      >
        {logoContent}
      </Link>
    );
  }

  return logoContent;
};

export default Logo;