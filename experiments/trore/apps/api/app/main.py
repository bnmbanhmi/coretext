from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routers import listings
from .database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")
    yield

app = FastAPI(title="Trore API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], # Allow local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(listings.router)

@app.get("/")
async def root():
    return {"message": "Hello Trore API"}
