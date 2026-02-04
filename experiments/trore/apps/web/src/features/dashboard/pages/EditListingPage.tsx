import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { ListingForm } from '../../admin/components/ListingForm';
import { useListingDetails } from '../../admin/api/useListingDetails';
import { useUpdateListing } from '../../admin/api/useUpdateListing';
import { ListingCreate } from '@trore/types';

export const EditListingPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const { data: listing, isLoading: isLoadingListing, error: loadError } = useListingDetails(id);
  const { mutate, isPending, error: updateError } = useUpdateListing(id || '');

  if (isLoadingListing) return <div>Loading...</div>;
  if (loadError) return <div>Error loading listing: {(loadError as Error).message}</div>;
  if (!listing) return <div>Listing not found</div>;

  const handleSubmit = (data: ListingCreate) => {
    // Pass only the fields that are part of ListingCreate to avoid sending 'id', 'created_at', etc. if they are in data
    // But ListingForm only outputs the fields defined in zod schema, which matches ListingCreate.
    mutate(data, {
      onSuccess: () => {
        toast.success('Listing Updated Successfully');
        navigate(`/listings/${id}`); 
      }
    });
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Edit Listing</h1>
      <ListingForm 
        initialValues={listing}
        onSubmit={handleSubmit} 
        isPending={isPending} 
        error={updateError}
        submitLabel="Save Changes"
      />
    </div>
  );
};
