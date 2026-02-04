import React from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { ListingForm } from '../components/ListingForm';
import { useCreateListing } from '../api/useCreateListing';

export const NewListingPage: React.FC = () => {
  const navigate = useNavigate();

  const { mutate, isPending, error } = useCreateListing({
    onSuccess: (data) => {
      toast.success('Listing Created Successfully');
      if (data?.id) {
          // Redirect to detail page
          navigate(`/listings/${data.id}`);
      } else {
          navigate('/admin/listings');
      }
    },
  });

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Create New Listing</h1>
      <ListingForm 
        onSubmit={mutate} 
        isPending={isPending} 
        error={error} 
        submitLabel="Create Listing"
      />
    </div>
  );
};