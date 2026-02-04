import { render, screen } from '@testing-library/react'
import { ListingCard } from './ListingCard'
import { describe, it, expect } from 'vitest'

describe('ListingCard', () => {
  const mockListing = {
    id: '123',
    title: 'Test Listing',
    price: 5000000,
    area_sqm: 30.5,
    address: '123 Test St',
    status: 'AVAILABLE'
  }

  it('renders listing details correctly', () => {
    render(<ListingCard listing={mockListing} />)
    
    expect(screen.getByText('Test Listing')).toBeInTheDocument()
    expect(screen.getByText('5.0 million/month')).toBeInTheDocument()
    expect(screen.getByText('30.5 m² • 123 Test St')).toBeInTheDocument()
    expect(screen.getByRole('img')).toHaveAttribute('src', 'https://placehold.co/600x400?text=Property')
  })
})
