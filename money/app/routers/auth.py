from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import dependencies
from app.models import User
from app.utils.security import create_session_token, verify_password

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request, "error": None})


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(dependencies.get_db_dep),
    settings=Depends(dependencies.get_settings_dep),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=400,
        )
    token = create_session_token(user.id, settings.secret_key)
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(settings.session_cookie_name, token, httponly=True, max_age=60 * 60 * 12)
    return response


@router.post("/logout")
def logout(settings=Depends(dependencies.get_settings_dep)):
    resp = RedirectResponse(url="/auth/login", status_code=303)
    resp.delete_cookie(settings.session_cookie_name)
    return resp
