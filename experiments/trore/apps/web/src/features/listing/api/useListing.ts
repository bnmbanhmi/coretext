import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api';
import { Listing } from '@trore/types';

export const useListing = (id: string) => {
  return useQuery({
    queryKey: ['listings', id],
    queryFn: async () => {
      return apiClient.get<Listing>(`/listings/${id}`);
    },
    enabled: !!id,
  });
};
