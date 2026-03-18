from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Basic FastAPI Demo - Descope",
    version="0.1.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": f"API is running"}
