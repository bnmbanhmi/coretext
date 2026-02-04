import React from 'react';
import { Listing } from '@trore/types';
import { formatPrice, formatArea } from '../../../lib/format';

interface ListingDetailProps {
  listing: Listing;
  onEdit?: () => void;
}

export const ListingDetail: React.FC<ListingDetailProps> = ({ listing, onEdit }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 max-w-4xl mx-auto relative">
       {onEdit && (
         <button 
           onClick={onEdit}
           className="absolute top-6 right-6 px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 border transition-colors"
         >
           Edit Listing
         </button>
       )}
       
       <h1 className="text-3xl font-bold mb-4 text-gray-900 pr-32">{listing.title}</h1>
       
       <div className="flex flex-col md:flex-row md:items-end md:justify-between mb-6 border-b pb-6">
         <div>
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {formatPrice(listing.price)}
            </div>
            <div className="text-gray-600 text-lg">
               {formatArea(listing.area_sqm)} • {listing.address}
            </div>
         </div>
         <div className="mt-4 md:mt-0 text-sm text-gray-500">
           ID: {listing.id}
         </div>
       </div>

       <div className="mb-8">
         <h2 className="text-xl font-semibold mb-3 text-gray-900">Description</h2>
         <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
           {listing.description || "No description provided."}
         </p>
       </div>

       {listing.attributes && Object.keys(listing.attributes).length > 0 && (
         <div>
            <h2 className="text-xl font-semibold mb-3 text-gray-900">Features</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
               {Object.entries(listing.attributes).map(([key, value]) => (
                 <div key={key} className="flex justify-between items-center p-3 bg-gray-50 rounded border border-gray-100">
                   <span className="font-medium text-gray-700 capitalize">{key.replace(/_/g, ' ')}</span>
                   <span className="text-gray-900 font-semibold">
                     {value === true ? 'Yes' : value === false ? 'No' : String(value)}
                   </span>
                 </div>
               ))}
            </div>
         </div>
       )}
    </div>
  );
};