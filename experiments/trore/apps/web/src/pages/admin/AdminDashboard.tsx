import { Link } from 'react-router-dom';
import { useListings, useDeleteListing } from '../../features/admin/hooks/useAdminListings';

export default function AdminDashboard() {
  const { data: listings, isLoading, error } = useListings();
  const deleteMutation = useDeleteListing();

  if (isLoading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-500">Error loading listings</div>;

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this listing?')) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (e) {
        alert('Failed to delete');
      }
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Admin Listings Dashboard</h1>
        <Link 
            to="/new-listing" 
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
            Create New
        </Link>
      </div>

      <div className="overflow-x-auto bg-white shadow-md rounded-lg">
        <table className="min-w-full leading-normal">
          <thead>
            <tr>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                ID
              </th>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Title
              </th>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Price
              </th>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Area
              </th>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Status
              </th>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Created At
              </th>
              <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {listings?.map((listing) => (
              <tr key={listing.id}>
                <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                  <span className="text-gray-900 whitespace-no-wrap" title={listing.id}>
                    {listing.id.substring(0, 8)}...
                  </span>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                  <p className="text-gray-900 whitespace-no-wrap font-medium">{listing.title}</p>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                  <p className="text-gray-900 whitespace-no-wrap">
                    {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(listing.price)}
                  </p>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                  <p className="text-gray-900 whitespace-no-wrap">{listing.area_sqm} m²</p>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                  <span className={`relative inline-block px-3 py-1 font-semibold leading-tight rounded-full ${
                      listing.status === 'AVAILABLE' ? 'bg-green-200 text-green-900' :
                      listing.status === 'DRAFT' ? 'bg-gray-200 text-gray-900' :
                      'bg-red-200 text-red-900'
                  }`}>
                    <span aria-hidden className="absolute inset-0 opacity-50 rounded-full"></span>
                    <span className="relative text-xs">{listing.status}</span>
                  </span>
                </td>
                 <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                  <p className="text-gray-900 whitespace-no-wrap">
                    {listing.created_at ? new Date(listing.created_at).toLocaleDateString() : '-'}
                  </p>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                  <div className="flex gap-2">
                    <Link 
                      to={`/admin/listings/${listing.id}/edit`}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Edit
                    </Link>
                    <button 
                      onClick={() => handleDelete(listing.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {listings && listings.length === 0 && (
                <tr>
                    <td colSpan={7} className="px-5 py-5 border-b border-gray-200 bg-white text-sm text-center">
                        No listings found
                    </td>
                </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
