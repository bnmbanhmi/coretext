import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ListingForm } from './ListingForm';
import { describe, it, expect, vi } from 'vitest';

describe('ListingForm', () => {
  it('renders form fields', () => {
    render(<ListingForm onSubmit={vi.fn()} isPending={false} />);
    expect(screen.getByLabelText(/Title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Price/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Area/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Address/i)).toBeInTheDocument();
  });

  it('shows validation error for negative price', async () => {
    const mockSubmit = vi.fn();
    render(<ListingForm onSubmit={mockSubmit} isPending={false} />);
    
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Valid Title' } });
    fireEvent.change(screen.getByLabelText(/Price/i), { target: { value: '-100' } });
    fireEvent.change(screen.getByLabelText(/Area/i), { target: { value: '30' } });
    fireEvent.change(screen.getByLabelText(/Address/i), { target: { value: '123 Street' } });

    fireEvent.click(screen.getByRole('button', { name: /Create/i }));

    await waitFor(() => {
      expect(screen.getByText(/Price must be positive/i)).toBeInTheDocument();
    });
    
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it('submits valid data', async () => {
    const mockSubmit = vi.fn();
    render(<ListingForm onSubmit={mockSubmit} isPending={false} />);
    
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Valid Title' } });
    fireEvent.change(screen.getByLabelText(/Price/i), { target: { value: '5000000' } });
    fireEvent.change(screen.getByLabelText(/Area/i), { target: { value: '30' } });
    fireEvent.change(screen.getByLabelText(/Address/i), { target: { value: '123 Street' } });

    fireEvent.click(screen.getByRole('button', { name: /Create/i }));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({
        title: 'Valid Title',
        price: 5000000,
        area_sqm: 30,
        address: '123 Street',
        status: 'AVAILABLE'
      }), expect.anything());
    });
  });

  it('populates with initial values', () => {
    const initialValues = {
      title: 'Existing Listing',
      price: 1000000,
      area_sqm: 50,
      address: 'Old Address',
    };
    render(<ListingForm onSubmit={vi.fn()} isPending={false} initialValues={initialValues} />);

    expect(screen.getByLabelText(/Title/i)).toHaveValue('Existing Listing');
    expect(screen.getByLabelText(/Price/i)).toHaveValue(1000000);
    expect(screen.getByLabelText(/Area/i)).toHaveValue(50);
    expect(screen.getByLabelText(/Address/i)).toHaveValue('Old Address');
  });
});