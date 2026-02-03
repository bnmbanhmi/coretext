from fastapi import FastAPI

app = FastAPI(title="Trore API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Trore API"}
