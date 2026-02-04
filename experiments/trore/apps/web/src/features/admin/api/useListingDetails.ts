import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api';
import { Listing } from '@trore/types';

export const useListingDetails = (id: string | undefined) => {
  return useQuery({
    queryKey: ['listings', id],
    queryFn: () => apiClient.get<Listing>(`/listings/${id}`),
    enabled: !!id,
  });
};
