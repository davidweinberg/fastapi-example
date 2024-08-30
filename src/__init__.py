from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db

# fast api server
version = "v1"
@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"server is starting ... ")
    await init_db()
    yield
    print(f"server has been stopped")

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version=version,
    lifespan=life_span
)
app.include_router(book_router, prefix="/api/{version}/books", tags=["Books"])
