import { render, screen } from '@testing-library/react';
import { ListingGrid } from './ListingGrid';
import { Listing, ListingStatus } from '@trore/types';
import { describe, it, expect } from 'vitest';

describe('ListingGrid', () => {
  it('renders "No listings found" when empty', () => {
    render(<ListingGrid listings={[]} />);
    expect(screen.getByText('No listings found.')).toBeInTheDocument();
  });

  it('renders cards for listings', () => {
    const listings: Listing[] = [
      {
        id: '1',
        title: 'L1',
        price: 1000,
        area_sqm: 10,
        address: 'A1',
        status: ListingStatus.AVAILABLE,
        attributes: {},
        createdAt: '',
        updatedAt: ''
      },
      {
        id: '2',
        title: 'L2',
        price: 2000,
        area_sqm: 20,
        address: 'A2',
        status: ListingStatus.AVAILABLE,
        attributes: {},
        createdAt: '',
        updatedAt: ''
      }
    ];
    render(<ListingGrid listings={listings} />);
    expect(screen.getByText('L1')).toBeInTheDocument();
    expect(screen.getByText('L2')).toBeInTheDocument();
  });
});
