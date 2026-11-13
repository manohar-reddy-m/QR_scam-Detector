import { describe, it, expect } from 'vitest';
import { apiClient } from '../api/client';

describe('API Client Configuration', () => {
  it('has valid timeout and headers', () => {
    expect(apiClient.defaults.timeout).toBe(60000);
    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('has default baseURL configured', () => {
    expect(apiClient.defaults.baseURL).toBeDefined();
  });
});

