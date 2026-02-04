import { render, screen } from '@testing-library/react';
import { ListingDetail } from './ListingDetail';
import { Listing, ListingStatus } from '@trore/types';
import { describe, it, expect } from 'vitest';

const mockListing: Listing = {
  id: '123',
  title: 'Test Listing',
  description: 'Test Description',
  price: 1000000,
  area_sqm: 50,
  address: '123 Test St',
  status: ListingStatus.AVAILABLE,
  attributes: {
    wifi: true,
    balcony: false,
    parking: 'Street'
  },
  created_at: '2023-01-01',
  updated_at: '2023-01-01'
};

describe('ListingDetail', () => {
  it('renders listing details correctly', () => {
    render(<ListingDetail listing={mockListing} />);
    
    expect(screen.getByText('Test Listing')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    expect(screen.getByText('123 Test St', { exact: false })).toBeInTheDocument();
  });

  it('renders attributes correctly', () => {
    render(<ListingDetail listing={mockListing} />);
    
    expect(screen.getByText('Wifi')).toBeInTheDocument();
    expect(screen.getByText('Yes')).toBeInTheDocument();
    
    expect(screen.getByText('Balcony')).toBeInTheDocument();
    expect(screen.getByText('No')).toBeInTheDocument();
    
    expect(screen.getByText('Parking')).toBeInTheDocument();
    expect(screen.getByText('Street')).toBeInTheDocument();
  });
});
