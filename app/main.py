from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.routes import router
from app.db_utils import init_db, seed_users


def startup_event():
    init_db()
    seed_users()


@asynccontextmanager
async def lifespan(_: FastAPI):
    startup_event()
    yield


app = FastAPI(
    title="Basic FastAPI Demo - Descope",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/")
async def root():
    return {"message": f"API is running"}
