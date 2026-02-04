import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ListingStatus } from '@trore/types';

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  price: z.coerce.number().positive('Price must be positive'),
  area_sqm: z.coerce.number().positive('Area must be positive'),
  address: z.string().min(1, 'Address is required'),
  status: z.nativeEnum(ListingStatus).optional(),
});

type FormData = z.infer<typeof schema>;

interface ListingFormProps {
  initialValues?: Partial<FormData>;
  onSubmit: (data: FormData) => void;
  isPending: boolean;
  error?: Error | null;
  submitLabel?: string;
}

export const ListingForm: React.FC<ListingFormProps> = ({ 
  initialValues, 
  onSubmit, 
  isPending, 
  error,
  submitLabel = 'Create'
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: initialValues,
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-w-lg mx-auto p-4 border rounded shadow bg-white">
      {error && <div className="text-red-500 mb-4">Error: {error.message}</div>}
      
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
        <label htmlFor="description" className="block text-sm font-medium">Description</label>
        <textarea
          id="description"
          {...register('description')}
          className="mt-1 block w-full border rounded p-2"
          rows={3}
        />
        {errors.description && <p className="text-red-500 text-sm">{errors.description.message}</p>}
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

      {/* Only show status if initialValues (Edit Mode) or if we want to allow setting status on create. 
          The requirement implies status management for existing listings. 
          "Given a listing is currently "AVAILABLE" ... When I change the status ..."
      */}
      <div>
        <label htmlFor="status" className="block text-sm font-medium">Status</label>
        <select
          id="status"
          {...register('status')}
          className="mt-1 block w-full border rounded p-2"
          defaultValue={ListingStatus.AVAILABLE}
        >
          {Object.values(ListingStatus).map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
        {errors.status && <p className="text-red-500 text-sm">{errors.status.message}</p>}
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {isPending ? 'Saving...' : submitLabel}
      </button>
    </form>
  );
};