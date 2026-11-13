import { apiClient } from './client';
import type {
  QRAnalyzeResponse,
  QRDecodeOnlyResponse,
  QRDistortResponse,
  QRCompareResponse,
} from '../types';

export async function analyzeQRCode(file: File): Promise<QRAnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post<QRAnalyzeResponse>(
    '/api/v1/qr/analyze',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return response.data;
}

export async function decodeQRCode(file: File): Promise<QRDecodeOnlyResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post<QRDecodeOnlyResponse>(
    '/api/v1/qr/decode',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return response.data;
}

export async function distortQRCode(
  file: File,
  severity: number = 0.5
): Promise<QRDistortResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('severity', String(severity));
  const response = await apiClient.post<QRDistortResponse>(
    '/api/v1/qr/distort',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return response.data;
}

export async function compareQRCodes(
  file1: File,
  file2: File
): Promise<QRCompareResponse> {
  const formData = new FormData();
  formData.append('file1', file1);
  formData.append('file2', file2);
  const response = await apiClient.post<QRCompareResponse>(
    '/api/v1/qr/compare',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return response.data;
}

export interface QRSample {
  id: string;
  title: string;
  category: 'LOW RISK' | 'MEDIUM RISK' | 'HIGH RISK';
  badge_color: 'emerald' | 'amber' | 'rose';
  description: string;
  payload: string;
  data_url: string;
}

export async function getQRSamples(): Promise<QRSample[]> {
  const response = await apiClient.get<{ success: boolean; samples: QRSample[] }>('/api/v1/qr/samples');
  return response.data.samples;
}

export async function generateQRCode(text: string): Promise<{ success: boolean; payload: string; data_url: string }> {
  const response = await apiClient.post<{ success: boolean; payload: string; data_url: string }>(
    '/api/v1/qr/generate',
    { text }
  );
  return response.data;
}
