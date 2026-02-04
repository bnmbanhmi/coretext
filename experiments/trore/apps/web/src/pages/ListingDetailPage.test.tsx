import { render, screen } from '@testing-library/react'
import ListingDetailPage from './ListingDetailPage'
import { vi, describe, it, expect, Mock } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import * as useListingHook from '../hooks/useListing'
import '@testing-library/jest-dom'

// Mock useListing
vi.mock('../hooks/useListing')

describe('ListingDetailPage', () => {
  it('renders loading state', () => {
    (useListingHook.useListing as Mock).mockReturnValue({
      listing: null,
      loading: true,
      error: null
    })

    render(
      <MemoryRouter initialEntries={['/listing/123']}>
        <Routes>
          <Route path="/listing/:id" element={<ListingDetailPage />} />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders error state', () => {
    (useListingHook.useListing as Mock).mockReturnValue({
      listing: null,
      loading: false,
      error: 'Listing not found'
    })

    render(
      <MemoryRouter initialEntries={['/listing/123']}>
        <Routes>
          <Route path="/listing/:id" element={<ListingDetailPage />} />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByText('Listing not found')).toBeInTheDocument()
    expect(screen.getByText('Return to Home')).toBeInTheDocument()
  })

  it('renders listing details', () => {
    const mockListing = {
      id: '123',
      title: 'Test House',
      description: 'Nice house',
      price: 1000,
      area_sqm: 50,
      address: '123 St',
      attributes: { pool: 'yes' },
      status: 'AVAILABLE',
      created_at: '2023-01-01'
    };

    (useListingHook.useListing as Mock).mockReturnValue({
      listing: mockListing,
      loading: false,
      error: null
    })

    render(
      <MemoryRouter initialEntries={['/listing/123']}>
        <Routes>
          <Route path="/listing/:id" element={<ListingDetailPage />} />
        </Routes>
      </MemoryRouter>
    )
    
    expect(screen.getByText('Test House')).toBeInTheDocument()
    expect(screen.getByText('123 St')).toBeInTheDocument()
    expect(screen.getByText('$1,000')).toBeInTheDocument()
    expect(screen.getByText('50 m²')).toBeInTheDocument()
    expect(screen.getByText('Nice house')).toBeInTheDocument()
    expect(screen.getByText('pool:')).toBeInTheDocument()
  })
})
