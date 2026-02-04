import { useState, useEffect } from 'react'
import { ListingCard, Listing } from '../components/ListingCard'
import './HomePage.css'

export default function HomePage() {
    const [listings, setListings] = useState<Listing[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [searchTerm, setSearchTerm] = useState('')

    const fetchListings = async (query?: string) => {
        setLoading(true)
        setError(null)
        try {
            const url = new URL('http://localhost:8000/listings')
            if (query) {
                url.searchParams.append('q', query)
            }
            // limit default is 20
            
            const res = await fetch(url.toString())
            if (!res.ok) throw new Error('Failed to fetch listings')
            
            const data = await res.json()
            setListings(data)
        } catch (err) {
            setError('Failed to load listings')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchListings()
    }, [])

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        fetchListings(searchTerm)
    }

    return (
        <div className="home-page">
            <div className="search-bar-container">
                <form onSubmit={handleSearch} className="search-form">
                    <input 
                        type="text" 
                        placeholder="Search listings..." 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="search-input"
                    />
                    <button type="submit" className="search-button">Search</button>
                </form>
            </div>

            {loading && <div className="loading">Loading...</div>}
            {error && <div className="error">{error}</div>}
            
            {!loading && !error && listings.length === 0 && (
                <div className="empty-state">No properties found</div>
            )}

            <div className="listings-grid">
                {listings.map(listing => (
                    <ListingCard key={listing.id} listing={listing} />
                ))}
            </div>
        </div>
    )
}