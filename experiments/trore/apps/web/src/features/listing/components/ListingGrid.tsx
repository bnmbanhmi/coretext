import React from 'react';
import { Listing } from '@trore/types';
import { ListingCard } from './ListingCard';

interface ListingGridProps {
  listings: Listing[];
}

export const ListingGrid: React.FC<ListingGridProps> = ({ listings }) => {
  if (!listings || listings.length === 0) {
    return <div className="text-center py-10 text-gray-500">No listings found.</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {listings.map((listing) => (
        <ListingCard key={listing.id} listing={listing} />
      ))}
    </div>
  );
};
