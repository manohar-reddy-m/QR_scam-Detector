import { useQuery } from '@tanstack/react-query';
import { getModelStatus, getModelMetrics } from '../api/model';

export function useModelStatus() {
  return useQuery({
    queryKey: ['modelStatus'],
    queryFn: getModelStatus,
    staleTime: 60000,
  });
}

export function useModelMetrics() {
  return useQuery({
    queryKey: ['modelMetrics'],
    queryFn: getModelMetrics,
    staleTime: 60000,
  });
}
