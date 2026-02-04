import { render, screen } from '@testing-library/react'
import FeaturesList from './FeaturesList'
import { describe, it, expect } from 'vitest'
import '@testing-library/jest-dom'

describe('FeaturesList', () => {
  it('renders nothing when attributes are null or empty', () => {
    const { container } = render(<FeaturesList attributes={null} />)
    expect(container).toBeEmptyDOMElement()
    
    const { container: container2 } = render(<FeaturesList attributes={{}} />)
    expect(container2).toBeEmptyDOMElement()
  })

  it('renders attributes list correctly', () => {
    const attrs = {
      wifi: "yes",
      balcony: "no",
      floor: 2
    }
    render(<FeaturesList attributes={attrs} />)
    
    expect(screen.getByText('Features')).toBeInTheDocument()
    expect(screen.getByText('wifi:')).toBeInTheDocument()
    expect(screen.getByText('yes')).toBeInTheDocument()
    expect(screen.getByText('balcony:')).toBeInTheDocument()
    expect(screen.getByText('no')).toBeInTheDocument()
    expect(screen.getByText('floor:')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('formats keys with underscores', () => {
    render(<FeaturesList attributes={{ air_conditioning: "yes" }} />)
    expect(screen.getByText('air conditioning:')).toBeInTheDocument()
  })
})
