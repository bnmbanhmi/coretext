import { useParams, useNavigate } from 'react-router-dom';
import { useListing, useUpdateListing } from '../../features/admin/hooks/useAdminListings';
import ListingForm, { ListingFormData } from '../../components/ListingForm';
import { useState } from 'react';

export default function EditListingPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: listing, isLoading, error } = useListing(id || '');
  const updateMutation = useUpdateListing();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (isLoading) return <div className="p-6">Loading listing data...</div>;
  if (error || !listing) return <div className="p-6 text-red-500">Error loading listing</div>;

  const handleSubmit = async (data: ListingFormData) => {
    setErrorMessage(null);
    try {
      await updateMutation.mutateAsync({
        id: id!,
        data: {
            title: data.title,
            price: Number(data.price),
            area: Number(data.area),
            address: data.address,
            status: data.status
        }
      });
      // Redirect to admin dashboard
      navigate('/admin/listings');
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to update listing");
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Edit Listing</h1>
      {errorMessage && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{errorMessage}</div>}
      
      <div className="bg-white p-6 shadow rounded-lg">
        <ListingForm 
            initialValues={{
                title: listing.title,
                price: listing.price,
                area: listing.area_sqm,
                address: listing.address,
                status: listing.status
            }}
            onSubmit={handleSubmit}
            submitLabel="Save Changes"
            isLoading={updateMutation.isPending}
        />
      </div>
    </div>
  );
}
