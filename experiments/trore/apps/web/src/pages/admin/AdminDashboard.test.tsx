import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AdminDashboard from './AdminDashboard';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('AdminDashboard', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    global.fetch = vi.fn();
    window.confirm = vi.fn(() => true); // Mock confirm
  });

  it('renders listings', async () => {
    const mockListings = [{
      id: '1',
      title: 'Admin House',
      price: 100,
      area_sqm: 50,
      address: 'Admin St',
      status: 'DRAFT',
      created_at: '2023-01-01'
    }];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockListings
    });

    render(<AdminDashboard />, { wrapper: createWrapper() });

    await waitFor(() => expect(screen.getByText('Admin House')).toBeInTheDocument());
    expect(screen.getByText('DRAFT')).toBeInTheDocument();
  });

  it('handles delete', async () => {
    const mockListings = [{
      id: '1',
      title: 'Delete Me',
      price: 100,
      area_sqm: 50,
      address: 'Admin St',
      status: 'AVAILABLE'
    }];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockListings
    });

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
    }); // Delete response

    // After delete, it refetches
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => []
    });

    render(<AdminDashboard />, { wrapper: createWrapper() });

    await waitFor(() => expect(screen.getByText('Delete Me')).toBeInTheDocument());

    const deleteBtn = screen.getByText('Delete');
    fireEvent.click(deleteBtn);

    expect(window.confirm).toHaveBeenCalled();
    
    await waitFor(() => expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/listings/1'), expect.objectContaining({ method: 'DELETE' })));
  });
});
