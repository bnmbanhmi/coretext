import { useState, useEffect } from 'react';

export interface ListingFormData {
  title: string;
  price: string | number;
  area: string | number;
  address: string;
  status?: string;
}

interface ListingFormProps {
  initialValues?: ListingFormData;
  onSubmit: (data: ListingFormData) => Promise<void>;
  submitLabel?: string;
  isLoading?: boolean;
}

export default function ListingForm({ initialValues, onSubmit, submitLabel = 'Submit', isLoading = false }: ListingFormProps) {
  const [formData, setFormData] = useState<ListingFormData>({
    title: '',
    price: '',
    area: '',
    address: '',
    status: 'DRAFT'
  });

  useEffect(() => {
    if (initialValues) {
        setFormData({
            title: initialValues.title || '',
            price: initialValues.price || '',
            area: initialValues.area || '',
            address: initialValues.address || '',
            status: initialValues.status || 'DRAFT'
        });
    }
  }, [initialValues]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-lg">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title</label>
        <input
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
        />
      </div>
      <div>
        <label htmlFor="price" className="block text-sm font-medium text-gray-700">Price</label>
        <input
          id="price"
          name="price"
          type="number"
          value={formData.price}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
        />
      </div>
      <div>
        <label htmlFor="area" className="block text-sm font-medium text-gray-700">Area (sqm)</label>
        <input
          id="area"
          name="area"
          type="number"
          step="0.1"
          value={formData.area}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
        />
      </div>
      <div>
        <label htmlFor="address" className="block text-sm font-medium text-gray-700">Address</label>
        <input
          id="address"
          name="address"
          value={formData.address}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
        />
      </div>
      {/* Optional Status Field - only show if initialValues provided (Edit Mode) */}
      {initialValues && (
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
            <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
            >
                <option value="DRAFT">Draft</option>
                <option value="AVAILABLE">Available</option>
                <option value="RENTED">Rented</option>
                <option value="ARCHIVED">Archived</option>
            </select>
          </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-300"
      >
        {isLoading ? 'Saving...' : submitLabel}
      </button>
    </form>
  );
}
