import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCreateListing } from '../api/useCreateListing';

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  price: z.coerce.number().positive('Price must be positive'),
  area_sqm: z.coerce.number().positive('Area must be positive'),
  address: z.string().min(1, 'Address is required'),
});

type FormData = z.infer<typeof schema>;

// Need to import Listing type. For now using any or defining locally if import fails.
// Assuming the hook returns the data which matches our Listing interface
export const ListingForm: React.FC<{ onSuccess?: (data: any) => void }> = ({ onSuccess }) => {
  const { mutate, isPending, error } = useCreateListing({
    onSuccess: (data) => {
      onSuccess?.(data);
    },
  });
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-w-lg mx-auto p-4 border rounded shadow">
      {error && <div className="text-red-500 mb-4">Error creating listing: {error.message}</div>}
      
      <div>
        <label htmlFor="title" className="block text-sm font-medium">Title</label>
        <input
          id="title"
          {...register('title')}
          className="mt-1 block w-full border rounded p-2"
        />
        {errors.title && <p className="text-red-500 text-sm">{errors.title.message}</p>}
      </div>

      <div>
        <label htmlFor="price" className="block text-sm font-medium">Price</label>
        <input
          id="price"
          type="number"
          {...register('price')}
          className="mt-1 block w-full border rounded p-2"
        />
        {errors.price && <p className="text-red-500 text-sm">{errors.price.message}</p>}
      </div>

      <div>
        <label htmlFor="area_sqm" className="block text-sm font-medium">Area (sqm)</label>
        <input
          id="area_sqm"
          type="number"
          {...register('area_sqm')}
          className="mt-1 block w-full border rounded p-2"
        />
        {errors.area_sqm && <p className="text-red-500 text-sm">{errors.area_sqm.message}</p>}
      </div>

      <div>
        <label htmlFor="address" className="block text-sm font-medium">Address</label>
        <input
          id="address"
          {...register('address')}
          className="mt-1 block w-full border rounded p-2"
        />
        {errors.address && <p className="text-red-500 text-sm">{errors.address.message}</p>}
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {isPending ? 'Creating...' : 'Create'}
      </button>
    </form>
  );
};
