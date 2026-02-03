import { render, screen, fireEvent } from '@testing-library/react'
import NewListingPage from './NewListingPage'
import { vi } from 'vitest'

describe('NewListingPage', () => {
  it('renders the form correctly', () => {
    render(<NewListingPage />)
    expect(screen.getByLabelText(/Title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Price/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Area/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Address/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Create/i })).toBeInTheDocument()
  })

  it('validates negative price', async () => {
    render(<NewListingPage />)
    
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'Test' } })
    fireEvent.change(screen.getByLabelText(/Price/i), { target: { value: '-100' } })
    fireEvent.change(screen.getByLabelText(/Area/i), { target: { value: '30' } })
    fireEvent.change(screen.getByLabelText(/Address/i), { target: { value: '123 St' } })
    
    const submitBtn = screen.getByRole('button', { name: /Create/i })
    fireEvent.click(submitBtn)
    
    expect(await screen.findByText(/Price must be a positive number/i)).toBeInTheDocument()
  })
})
