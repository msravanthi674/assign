from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.database import connect_db, close_db, get_database
from app.utils import seed_questions
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: connect DB on startup, close on shutdown."""
    connected = await connect_db()
    if connected:
        db = await get_database()
        await seed_questions(db)
    yield
    await close_db()


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

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
