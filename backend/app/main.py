from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, engine
from app.core.logging import setup_logging
from app.api.routes.documents import router as documents_router


setup_logging()

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Document Intelligence API",
    version="1.0.0"
)


BASE_DIR = Path(__file__).resolve().parents[2]

FRONTEND_DIR = BASE_DIR / "frontend"


app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR / "static"
    ),
    name="static"
)


app.include_router(documents_router)


@app.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False
)
def dashboard():

    html_file = (
        FRONTEND_DIR /
        "templates" /
        "dashboard.html"
    )

    return html_file.read_text(
        encoding="utf-8"
    )


@app.get(
    "/document-result",
    response_class=HTMLResponse,
    include_in_schema=False
)
def document_result():

    html_file = (
        FRONTEND_DIR /
        "templates" /
        "document_result.html"
    )

    return html_file.read_text(
        encoding="utf-8"
    )


@app.get("/api/v1/health")
def health():

    return {
        "status": "healthy",
        "service": "AI Document Intelligence API"
    }