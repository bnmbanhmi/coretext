import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ListingForm } from './ListingForm';
import { describe, it, expect, vi } from 'vitest';

// Mock the hook
const mockMutate = vi.fn();
vi.mock('../api/useCreateListing', () => ({
  useCreateListing: () => ({
    mutate: mockMutate,
    isPending: false,
    error: null,
  }),
}));

describe('ListingForm', () => {
  it('renders form fields', () => {
    render(<ListingForm />);
    expect(screen.getByLabelText(/Title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Price/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Area/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Address/i)).toBeInTheDocument();
  });

  it('shows validation error for negative price', async () => {
    render(<ListingForm />);
    
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Valid Title' } });
    fireEvent.change(screen.getByLabelText(/Price/i), { target: { value: '-100' } });
    fireEvent.change(screen.getByLabelText(/Area/i), { target: { value: '30' } });
    fireEvent.change(screen.getByLabelText(/Address/i), { target: { value: '123 Street' } });

    fireEvent.click(screen.getByRole('button', { name: /Create/i }));

    await waitFor(() => {
      expect(screen.getByText(/Price must be positive/i)).toBeInTheDocument();
    });
    
    expect(mockMutate).not.toHaveBeenCalled();
  });

  it('submits valid data', async () => {
    render(<ListingForm />);
    
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Valid Title' } });
    fireEvent.change(screen.getByLabelText(/Price/i), { target: { value: '5000000' } });
    fireEvent.change(screen.getByLabelText(/Area/i), { target: { value: '30' } });
    fireEvent.change(screen.getByLabelText(/Address/i), { target: { value: '123 Street' } });

    fireEvent.click(screen.getByRole('button', { name: /Create/i }));

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith(expect.objectContaining({
        title: 'Valid Title',
        price: 5000000,
        area_sqm: 30,
        address: '123 Street',
      }));
    });
  });
});
