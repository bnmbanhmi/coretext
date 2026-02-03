from fastapi import FastAPI
from app.api.v1.listings import router as listings_router

app = FastAPI(title="Trore API")

app.include_router(listings_router, prefix="/api/v1/listings", tags=["listings"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Trore API"}
