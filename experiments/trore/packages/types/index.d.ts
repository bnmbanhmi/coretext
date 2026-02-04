// Shared Types
export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export enum ListingStatus {
  DRAFT = "DRAFT",
  AVAILABLE = "AVAILABLE",
  RENTED = "RENTED",
  ARCHIVED = "ARCHIVED",
}

export interface ListingCreate {
  title: string;
  description?: string;
  price: number;
  area_sqm: number;
  address: string;
  status?: ListingStatus;
  attributes?: Record<string, any>;
}

export interface Listing extends BaseEntity {

  title: string;

  description?: string;

  price: number;

  area_sqm: number;

  address: string;

  status: ListingStatus;

  attributes: Record<string, any>;

}



export interface ListingSearchParams {

  skip?: number;

  limit?: number;

  status?: ListingStatus;

}
