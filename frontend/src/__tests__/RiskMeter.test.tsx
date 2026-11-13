import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RiskMeter } from '../components/ui/RiskMeter';

describe('RiskMeter component', () => {
  it('renders percentage score correctly for 85% risk', () => {
    render(<RiskMeter score={0.85} level="HIGH" />);
    expect(screen.getByText('85%')).toBeDefined();
    expect(screen.getByText('score')).toBeDefined();
  });

  it('renders percentage score correctly for 12% risk', () => {
    render(<RiskMeter score={0.12} level="LOW" />);
    expect(screen.getByText('12%')).toBeDefined();
  });
});

