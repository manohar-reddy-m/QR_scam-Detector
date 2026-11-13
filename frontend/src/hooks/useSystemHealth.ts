import { useQuery } from '@tanstack/react-query';
import { getSystemHealth } from '../api/system';

export function useSystemHealth() {
  return useQuery({
    queryKey: ['systemHealth'],
    queryFn: getSystemHealth,
    refetchInterval: 15000,
  });
}
