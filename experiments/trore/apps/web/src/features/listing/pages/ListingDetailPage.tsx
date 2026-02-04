import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useListing } from '../api/useListing';
import { ListingDetail } from '../components/ListingDetail';
import { NotFound } from '../../../components/NotFound';

export const ListingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: listing, isLoading, isError, error } = useListing(id || '');

  if (!id) {
    return <NotFound />;
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6 animate-pulse">
        <div className="h-10 bg-gray-200 rounded w-3/4 mb-6"></div>
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-8"></div>
        <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (isError) {
    // API client throws "API Error: Not Found" (404 usually)
    // Checking exact error object depends on axios/fetch setup.
    // In lib/api.ts: throw new Error(`API Error: ${response.statusText}`);
    // If 404, statusText is "Not Found".
    
    // We should improve api.ts to throw structured error, but for now string matching or assuming 404 if "Not Found" or "404" is in message.
    if ((error as Error).message.includes('404') || (error as Error).message.includes('Not Found')) {
        return <NotFound />;
    }
    
     // Also handle 422 (Unprocessable Entity) which happens for invalid UUIDs
    if ((error as Error).message.includes('422') || (error as Error).message.includes('Unprocessable')) {
         return <NotFound />;
    }

    return (
        <div className="text-center text-red-600 p-8">
            <h2 className="text-xl font-bold mb-2">Error loading listing</h2>
            <p>{(error as Error).message}</p>
        </div>
    );
  }

  if (!listing) {
      return <NotFound />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <ListingDetail 
        listing={listing} 
        onEdit={() => navigate(`/admin/listings/edit/${listing.id}`)}
      />
    </div>
  );
};