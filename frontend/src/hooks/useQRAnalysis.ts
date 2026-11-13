import { useMutation } from '@tanstack/react-query';
import { analyzeQRCode, decodeQRCode, distortQRCode, compareQRCodes } from '../api/qr';

export function useQRAnalyze() {
  return useMutation({
    mutationFn: (file: File) => analyzeQRCode(file),
  });
}

export function useQRDecode() {
  return useMutation({
    mutationFn: (file: File) => decodeQRCode(file),
  });
}

export function useQRDistort() {
  return useMutation({
    mutationFn: ({ file, severity }: { file: File; severity: number }) =>
      distortQRCode(file, severity),
  });
}

export function useQRCompare() {
  return useMutation({
    mutationFn: ({ file1, file2 }: { file1: File; file2: File }) =>
      compareQRCodes(file1, file2),
  });
}
