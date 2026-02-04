import { useState } from 'react'
import ListingForm, { ListingFormData } from '../components/ListingForm';

interface NewListingPageProps {
  onSuccess?: () => void
}

export default function NewListingPage({ onSuccess }: NewListingPageProps) {
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (data: ListingFormData) => {
    setError(null)
    setToast(null)

    const price = Number(data.price)
    const area = Number(data.area)

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
          title: data.title,
          price: Number(data.price),
          area: Number(data.area),
          address: data.address
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
    <div className="new-listing-page max-w-lg mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">New Listing</h2>
      {toast && <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">{toast}</div>}
      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}
      
      <ListingForm 
        onSubmit={handleSubmit} 
        submitLabel="Create"
        isLoading={loading}
      />
    </div>
  )
}