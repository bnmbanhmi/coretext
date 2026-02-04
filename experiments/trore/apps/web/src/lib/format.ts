export function formatPrice(price: number): string {
  if (price >= 1000000) {
    const millions = price / 1000000;
    // Check if it's a whole number to avoid unnecessary .0
    // But requirement says "X.X million/month", e.g. "5.0 million".
    return `${millions.toFixed(1)} million/month`;
  }
  return `${price.toLocaleString()}/month`;
}

export function formatArea(area: number): string {
  return `${Math.round(area)} m²`;
}
