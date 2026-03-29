from fastapi import FastAPI

from app.services.scheduler import shutdown_scheduler, start_scheduler


def register_scheduler(app: FastAPI) -> None:
    @app.on_event("startup")
    async def _startup():
        start_scheduler()

    @app.on_event("shutdown")
    async def _shutdown():
        shutdown_scheduler()
