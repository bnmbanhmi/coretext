import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api';
import { ListingCreate, Listing } from '@trore/types';

export const useCreateListing = (options?: { onSuccess?: (data: Listing) => void; onError?: (error: Error) => void }) => {
  const queryClient = useQueryClient();

  return useMutation<Listing, Error, ListingCreate>({
    mutationFn: (newListing) => apiClient.post<Listing>('/listings/', newListing),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['listings'] });
      options?.onSuccess?.(data);
    },
    onError: (error) => {
      options?.onError?.(error);
    },
  });
};