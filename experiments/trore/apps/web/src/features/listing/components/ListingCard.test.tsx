import { render, screen } from '@testing-library/react';
import { ListingCard } from './ListingCard';
import { Listing, ListingStatus } from '@trore/types';
import { describe, it, expect } from 'vitest';

const mockListing: Listing = {
  id: '1',
  title: 'Test Listing',
  price: 5000000,
  area_sqm: 30,
  address: '123 Test St',
  status: ListingStatus.AVAILABLE,
  attributes: {},
  createdAt: '2023-01-01',
  updatedAt: '2023-01-01'
};

describe('ListingCard', () => {
  it('renders listing details correctly', () => {
    render(<ListingCard listing={mockListing} />);
    
    expect(screen.getByText('Test Listing')).toBeInTheDocument();
    expect(screen.getByText('5.0 million/month')).toBeInTheDocument();
    expect(screen.getByText('30 m²')).toBeInTheDocument();
    expect(screen.getByText('123 Test St')).toBeInTheDocument();
  });

  it('formats large price correctly', () => {
    const expensiveListing = { ...mockListing, price: 10500000 };
    render(<ListingCard listing={expensiveListing} />);
    expect(screen.getByText('10.5 million/month')).toBeInTheDocument();
  });

  it('formats small price correctly', () => {
    const cheapListing = { ...mockListing, price: 500000 };
    render(<ListingCard listing={cheapListing} />);
    expect(screen.getByText('500,000/month')).toBeInTheDocument();
  });
});
