from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import dependencies
from app.background import register_scheduler
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import User
from app.routers import admin, auth, public, api
from app.seo import metadata
from app.utils.security import hash_password

settings = get_settings()
template_env = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))

def create_app() -> FastAPI:
    app = FastAPI(title=settings.project_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    static_path = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    app.include_router(public.router)
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(api.router)

    register_scheduler(app)

    @app.on_event("startup")
    def _startup():
        Base.metadata.create_all(bind=engine)
        _ensure_admin()
    @app.exception_handler(404)
    async def not_found(request: Request, exc):
        db = SessionLocal()
        try:
            runtime_settings = dependencies.build_runtime_settings(db)
        finally:
            db.close()
        return template_env.TemplateResponse(
            "public/errors/404.html",
            {"request": request, "settings": runtime_settings, "meta": metadata.default_meta()},
            status_code=404,
        )

    return app


def _ensure_admin() -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == settings.admin_email).first()
        if not user:
            user = User(email=settings.admin_email, hashed_password=hash_password(settings.admin_password))
            db.add(user)
            db.commit()
    finally:
        db.close()


app = create_app()
