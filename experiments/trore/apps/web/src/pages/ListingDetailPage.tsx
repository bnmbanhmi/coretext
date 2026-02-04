import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useListing } from '../hooks/useListing';
import FeaturesList from '../components/FeaturesList';

const ListingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { listing, loading, error } = useListing(id);

  if (loading) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-2xl font-bold text-red-600 mb-4">{error}</h2>
        <Link to="/" className="text-blue-500 hover:underline">Return to Home</Link>
      </div>
    );
  }

  if (!listing) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white shadow rounded-lg mt-6">
      <Link to="/" className="text-gray-500 hover:text-gray-700 mb-4 inline-block">&larr; Back to Listings</Link>
      
      <div className="border-b pb-4 mb-4">
        <h1 className="text-3xl font-bold text-gray-900">{listing.title}</h1>
        <p className="text-gray-600 text-lg">{listing.address}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <div className="text-3xl font-bold text-green-600 mb-2">
            ${listing.price.toLocaleString()}
          </div>
          <div className="text-gray-700">
             <span className="font-semibold">Area:</span> {listing.area_sqm} m²
          </div>
           {listing.description && (
            <div className="mt-4">
              <h3 className="text-xl font-semibold mb-2">Description</h3>
              <p className="text-gray-700 whitespace-pre-line">{listing.description}</p>
            </div>
          )}
        </div>
      </div>

      <FeaturesList attributes={listing.attributes} />
    </div>
  );
};

export default ListingDetailPage;
