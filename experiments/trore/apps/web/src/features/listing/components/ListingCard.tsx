import React from 'react';
import { Listing } from '@trore/types';
import { formatPrice, formatArea } from '../../../lib/format';

interface ListingCardProps {
  listing: Listing;
}

export const ListingCard: React.FC<ListingCardProps> = ({ listing }) => {
  return (
    <div className="border rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow bg-white flex flex-col h-full">
      <div className="bg-gray-200 h-48 w-full flex items-center justify-center shrink-0">
        {/* Placeholder image logic: In future, use listing.images[0] */}
        <span className="text-gray-400">No Image</span>
      </div>
      <div className="p-4 flex flex-col flex-grow">
        <h3 className="font-semibold text-lg line-clamp-2 mb-2" title={listing.title}>
          {listing.title}
        </h3>
        <div className="text-xl font-bold text-blue-600 mb-1">
          {formatPrice(listing.price)}
        </div>
        <div className="flex justify-between items-end text-sm text-gray-600 mt-auto">
          <span>{formatArea(listing.area_sqm)}</span>
          <span className="truncate max-w-[60%] text-right" title={listing.address}>
            {listing.address}
          </span>
        </div>
      </div>
    </div>
  );
};
