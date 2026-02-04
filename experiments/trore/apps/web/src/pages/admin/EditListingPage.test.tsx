import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import EditListingPage from './EditListingPage';

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
      <MemoryRouter initialEntries={['/admin/listings/1/edit']}>
        <Routes>
           <Route path="/admin/listings/:id/edit" element={children} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('EditListingPage', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    global.fetch = vi.fn();
  });

  it('loads and updates listing', async () => {
     const mockListing = {
      id: '1',
      title: 'Old Title',
      price: 100,
      area_sqm: 50,
      address: 'Old Addr',
      status: 'DRAFT'
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockListing
    });

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ...mockListing, title: 'New Title' })
    });

    render(<EditListingPage />, { wrapper: createWrapper() });

    await waitFor(() => expect(screen.getByDisplayValue('Old Title')).toBeInTheDocument());

    const titleInput = screen.getByLabelText('Title');
    fireEvent.change(titleInput, { target: { value: 'New Title' } });

    const saveBtn = screen.getByText('Save Changes');
    fireEvent.click(saveBtn);

    await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/listings/1'),
            expect.objectContaining({
                method: 'PUT',
                body: expect.stringContaining('New Title')
            })
        )
    });
  });
});
