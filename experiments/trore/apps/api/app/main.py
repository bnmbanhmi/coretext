from fastapi import FastAPI

app = FastAPI(title="Trore API")

@app.get("/")
async def root():
    return {"message": "Hello Trore API"}
