import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api';
import { Listing, ListingCreate } from '@trore/types';

export const useUpdateListing = (id: string) => {
  const queryClient = useQueryClient();

  return useMutation<Listing, Error, Partial<ListingCreate>>({
    mutationFn: (data) => apiClient.patch<Listing>(`/listings/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listings', id] });
      queryClient.invalidateQueries({ queryKey: ['listings'] });
    },
  });
};
