import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import HomePage from './HomePage'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'

describe('HomePage', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    global.fetch = vi.fn()
  })

  it('renders search bar and grid', async () => {
    (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => []
    })
    
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    )
    
    expect(screen.getByPlaceholderText('Search listings...')).toBeInTheDocument()
    // Wait for load
    await waitFor(() => expect(screen.getByText('No properties found')).toBeInTheDocument())
  })

  it('searches and displays results', async () => {
     const mockListings = [{
        id: '1',
        title: 'Nice House',
        price: 10000000,
        area_sqm: 100,
        address: 'Hanoi',
        status: 'AVAILABLE'
     }];
     
     // Initial load
     (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockListings
     });
     
     // Mock second call for search
     (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockListings
     })

     render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
     )
     
     await waitFor(() => expect(screen.getByText('Nice House')).toBeInTheDocument())
     
     // Search
     const input = screen.getByPlaceholderText('Search listings...')
     fireEvent.change(input, { target: { value: 'Nice' } })
     fireEvent.click(screen.getByText('Search'))
     
     // It should call fetch with q=Nice
     await waitFor(() => {
         expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('q=Nice'))
     })
  })
})
