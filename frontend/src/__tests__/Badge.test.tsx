import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RiskBadge, PayloadTypeBadge } from '../components/ui/Badge';

describe('RiskBadge component', () => {
  it('renders LOW risk badge correctly', () => {
    render(<RiskBadge level="LOW" />);
    expect(screen.getByText('LOW RISK')).toBeDefined();
  });

  it('renders HIGH risk badge correctly', () => {
    render(<RiskBadge level="HIGH" />);
    expect(screen.getByText('HIGH RISK')).toBeDefined();
  });

  it('renders INCONCLUSIVE badge correctly', () => {
    render(<RiskBadge level="INCONCLUSIVE" />);
    expect(screen.getByText('INCONCLUSIVE')).toBeDefined();
  });
});

describe('PayloadTypeBadge component', () => {
  it('renders URL_HTTPS payload type', () => {
    render(<PayloadTypeBadge type="URL_HTTPS" />);
    expect(screen.getByText('URL_HTTPS')).toBeDefined();
  });

  it('renders UPI_PAYMENT payload type', () => {
    render(<PayloadTypeBadge type="UPI_PAYMENT" />);
    expect(screen.getByText('UPI_PAYMENT')).toBeDefined();
  });
});

