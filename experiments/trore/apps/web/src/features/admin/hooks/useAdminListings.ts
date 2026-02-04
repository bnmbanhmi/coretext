import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_URL = 'http://localhost:8000/listings';

export interface Listing {
  id: string;
  title: string;
  description?: string;
  price: number;
  area_sqm: number;
  address: string;
  status: 'DRAFT' | 'AVAILABLE' | 'RENTED' | 'ARCHIVED';
  created_at?: string;
  attributes?: Record<string, any>;
}

export interface ListingUpdate {
  title?: string;
  description?: string;
  price?: number;
  area?: number;
  address?: string;
  status?: string;
  attributes?: Record<string, any>;
}

export const useListings = () => {
  return useQuery({
    queryKey: ['listings', 'admin'],
    queryFn: async (): Promise<Listing[]> => {
      const response = await fetch(`${API_URL}?admin_view=true`);
      if (!response.ok) {
        throw new Error('Failed to fetch listings');
      }
      return response.json();
    }
  });
};

export const useListing = (id: string) => {
  return useQuery({
    queryKey: ['listings', id],
    queryFn: async (): Promise<Listing> => {
      const response = await fetch(`${API_URL}/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch listing');
      }
      return response.json();
    },
    enabled: !!id
  });
};

export const useDeleteListing = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete listing');
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listings'] });
    }
  });
};

export const useUpdateListing = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: ListingUpdate }) => {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error('Failed to update listing');
      }
      return response.json();
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['listings'] });
      queryClient.invalidateQueries({ queryKey: ['listings', variables.id] });
    }
  });
};
