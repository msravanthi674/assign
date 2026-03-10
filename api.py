from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.database import connect_db, close_db, get_database
from app.utils import seed_questions
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    connected = connect_db()
    if connected:
        db = get_database()
        seed_questions(db)
    yield
    close_db()

app = FastAPI(
    title="AI-Driven Adaptive Diagnostic Engine",
    description=(
        "A 1D Adaptive Testing Prototype using Item Response Theory (IRT) "
        "and LLM-powered personalized study plans."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
