import React, { useState } from 'react';
import { useListings } from '../api/useListings';
import { ListingGrid } from '../components/ListingGrid';
import { ListingStatus } from '@trore/types';

export const ListingListPage: React.FC = () => {
  const [page, setPage] = useState(0);
  const pageSize = 20;

  const { data: listings, isLoading, error } = useListings({
    skip: page * pageSize,
    limit: pageSize,
    status: ListingStatus.AVAILABLE
  });

  const handleNext = () => setPage(p => p + 1);
  const handlePrev = () => setPage(p => Math.max(0, p - 1));

  if (isLoading) return <div className="p-8 text-center">Loading listings...</div>;
  if (error) return <div className="p-8 text-center text-red-500">Error loading listings</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Available Properties</h1>
      
      <ListingGrid listings={listings || []} />

      {/* Pagination Controls */}
      <div className="flex justify-center mt-8 gap-4">
        <button 
          onClick={handlePrev} 
          disabled={page === 0}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50 hover:bg-gray-300"
        >
          Previous
        </button>
        <span className="py-2">Page {page + 1}</span>
        <button 
          onClick={handleNext}
          disabled={!listings || listings.length < pageSize}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50 hover:bg-gray-300"
        >
          Next
        </button>
      </div>
    </div>
  );
};
