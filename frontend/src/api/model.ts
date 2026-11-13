import { apiClient } from './client';
import type { ModelStatusResponse, ModelMetricsResponse } from '../types';

export async function getModelStatus(): Promise<ModelStatusResponse> {
  const response = await apiClient.get<ModelStatusResponse>('/api/v1/model/status');
  return response.data;
}

export async function getModelMetrics(): Promise<ModelMetricsResponse> {
  const response = await apiClient.get<ModelMetricsResponse>('/api/v1/model/metrics');
  return response.data;
}
