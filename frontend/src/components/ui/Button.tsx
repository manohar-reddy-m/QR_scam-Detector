import React from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'cyber';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  children,
  disabled,
  className = '',
  ...props
}) => {
  const base =
    'inline-flex items-center justify-center font-medium rounded-md transition-colors duration-150 disabled:opacity-40 disabled:cursor-not-allowed select-none focus-visible:ring-2 focus-visible:ring-blue-500';

  const variants = {
    primary:   'bg-blue-600 hover:bg-blue-500 text-white',
    cyber:     'bg-blue-600 hover:bg-blue-500 text-white',
    secondary: 'bg-navy-800 hover:bg-navy-700 text-gray-200 border border-navy-700',
    danger:    'bg-rose-600 hover:bg-rose-500 text-white',
    ghost:     'bg-transparent hover:bg-navy-800 text-gray-400 hover:text-white',
  };

  const sizes = {
    sm: 'text-xs px-3 py-1.5 gap-1.5',
    md: 'text-sm px-4 py-2 gap-2',
    lg: 'text-sm px-5 py-2.5 gap-2',
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        icon && <span className="flex-shrink-0">{icon}</span>
      )}
      <span>{children}</span>
    </button>
  );
};
