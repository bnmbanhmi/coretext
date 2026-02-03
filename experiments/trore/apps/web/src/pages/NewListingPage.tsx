import { useState } from 'react'

interface NewListingPageProps {
  onSuccess?: () => void
}

export default function NewListingPage({ onSuccess }: NewListingPageProps) {
  const [formData, setFormData] = useState({
    title: '',
    price: '',
    area: '',
    address: ''
  })
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setToast(null)

    const price = parseInt(formData.price)
    const area = parseFloat(formData.area)

    if (isNaN(price) || price <= 0) {
      setError("Price must be a positive number")
      return
    }
    if (isNaN(area) || area <= 0) {
      setError("Area must be a positive number")
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/listings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: formData.title,
          price: price,
          area: area,
          address: formData.address
        })
      })

      if (!response.ok) {
        if (response.status === 503) {
            throw new Error("System is currently busy, please try again later")
        }
        throw new Error("Failed to create listing")
      }

      setToast("Listing Created Successfully")
      if (onSuccess) {
          setTimeout(onSuccess, 1000) // Delay for toast
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="new-listing-page">
      <h2>New Listing</h2>
      {toast && <div className="toast success">{toast}</div>}
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="title">Title</label>
          <input
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="price">Price</label>
          <input
            id="price"
            name="price"
            type="number"
            value={formData.price}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="area">Area (sqm)</label>
          <input
            id="area"
            name="area"
            type="number"
            step="0.1"
            value={formData.area}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="address">Address</label>
          <input
            id="address"
            name="address"
            value={formData.address}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Create'}
        </button>
      </form>
    </div>
  )
}
