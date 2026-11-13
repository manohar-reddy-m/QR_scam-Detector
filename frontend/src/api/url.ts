import { apiClient } from './client';
import type { URLAnalyzeResponse } from '../types';

export async function analyzeURL(url: string): Promise<URLAnalyzeResponse> {
  const response = await apiClient.post<URLAnalyzeResponse>('/api/v1/url/analyze', {
    url,
  });
  return response.data;
}
