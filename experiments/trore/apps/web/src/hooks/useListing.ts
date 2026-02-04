import { useState, useEffect } from 'react';

export interface Listing {
  id: string;
  title: string;
  description: string;
  price: number;
  area_sqm: number;
  address: string;
  attributes: Record<string, any>;
  status: string;
  created_at: string;
}

interface UseListingResult {
  listing: Listing | null;
  loading: boolean;
  error: string | null;
}

export const useListing = (id: string | undefined): UseListingResult => {
  const [listing, setListing] = useState<Listing | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
        setLoading(false);
        return;
    }

    const fetchListing = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/listings/${id}`);
        if (!response.ok) {
          if (response.status === 404) {
             throw new Error("Listing not found");
          }
          throw new Error("Failed to fetch listing");
        }
        const data = await response.json();
        setListing(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchListing();
  }, [id]);

  return { listing, loading, error };
};
