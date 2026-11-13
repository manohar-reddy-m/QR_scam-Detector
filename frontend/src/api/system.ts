import { apiClient } from './client';
import type { HealthResponse } from '../types';

export async function getSystemHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>('/api/v1/system/health');
  return response.data;
}
