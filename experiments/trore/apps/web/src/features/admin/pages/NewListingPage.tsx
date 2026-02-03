import React from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { ListingForm } from '../components/ListingForm';

export const NewListingPage: React.FC = () => {
  const navigate = useNavigate();

  const handleSuccess = (data: any) => {
    toast.success('Listing Created Successfully');
    if (data?.id) {
        navigate(`/admin/listings/${data.id}`);
    } else {
        navigate('/admin/listings');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Create New Listing</h1>
      {/* Passing a wrapper to handle data if I update ListingForm, or just redirect to list for now if ID is missing */}
      <ListingForm onSuccess={handleSuccess} />
    </div>
  );
};
