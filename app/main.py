from fastapi import FastAPI
from app.api.routes import router
from app.api.auth_routes import router as auth_router

app = FastAPI(
    title="Basic FastAPI Demo - Descope",
    version="0.1.0"
)

app.include_router(router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": f"API is running"}
