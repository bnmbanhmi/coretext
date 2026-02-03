import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../../lib/api';
// Assuming types are available, or I'll define locally if import fails
// import { ListingCreate, Listing } from '@trore/types'; 

// Local definition for now to avoid dependency issues immediately, will fix later if needed
interface ListingCreate {
  title: string;
  description?: string;
  price: number;
  area_sqm: number;
  address: string;
  attributes?: Record<string, any>;
}

interface Listing extends ListingCreate {
  id: string;
  status: string;
}

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
