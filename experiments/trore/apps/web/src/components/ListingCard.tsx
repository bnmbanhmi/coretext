export interface Listing {
    id: string
    title: string
    price: number
    area_sqm: number
    address: string
    status?: string
}

interface ListingCardProps {
    listing: Listing
}

export function ListingCard({ listing }: ListingCardProps) {
    const formatPrice = (price: number) => {
        // 5000000 -> 5.0 million/month
        const millions = (price / 1000000).toFixed(1)
        return `${millions} million/month`
    }

    return (
        <div className="listing-card">
            <img 
                src="https://placehold.co/600x400?text=Property" 
                alt={listing.title} 
                className="listing-image" 
            />
            <div className="listing-details">
                <h3>{listing.title}</h3>
                <p className="price">{formatPrice(listing.price)}</p>
                <p className="meta">{listing.area_sqm} m² • {listing.address}</p>
            </div>
        </div>
    )
}