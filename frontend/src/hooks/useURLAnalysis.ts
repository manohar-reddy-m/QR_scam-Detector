import { useMutation } from '@tanstack/react-query';
import { analyzeURL } from '../api/url';

export function useURLAnalyze() {
  return useMutation({
    mutationFn: (url: string) => analyzeURL(url),
  });
}
