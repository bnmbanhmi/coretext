import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api';
import { Listing, ListingSearchParams } from '@trore/types';

export const useListings = (params: ListingSearchParams) => {
  return useQuery({
    queryKey: ['listings', params],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
      if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
      if (params.status) searchParams.append('status', params.status);
      
      // apiClient.get returns Promise<T> which is Listing[]
      return apiClient.get<Listing[]>(`/listings/?${searchParams.toString()}`);
    },
  });
};
