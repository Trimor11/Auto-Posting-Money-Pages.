from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import dependencies
from app.models import Keyword, KeywordStatus, Page, PageStatus, PublishJob
from app.services.content_engine import ContentEngine
from app.services.keyword_manager import KeywordManager
from app.services.publisher import publish_ready_pages, rebuild_sitemap_cache
from app.services.settings_service import SettingsService

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    stats = {
        "keywords": db.query(Keyword).count(),
        "queued": db.query(Keyword).filter(Keyword.status == KeywordStatus.QUEUED).count(),
        "drafts": db.query(Page).filter(Page.status == PageStatus.DRAFT).count(),
        "published": db.query(Page).filter(Page.status == PageStatus.PUBLISHED).count(),
    }
    recent_pages = (
        db.query(Page)
        .order_by(Page.updated_at.desc())
        .limit(8)
        .all()
    )
    logs = db.execute(text("SELECT level, message, created_at FROM log_events ORDER BY created_at DESC LIMIT 10")).fetchall()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "stats": stats, "recent_pages": recent_pages, "logs": logs, "user": user},
    )


@router.get("/keywords", response_class=HTMLResponse)
def keyword_table(request: Request, db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    keywords = db.query(Keyword).order_by(Keyword.created_at.desc()).limit(100).all()
    return templates.TemplateResponse(
        "admin/keywords.html",
        {"request": request, "keywords": keywords, "user": user},
    )


@router.post("/keywords")
def add_keyword(
    phrase: str = Form(...),
    priority_score: float = Form(0),
    search_intent: str = Form("informational"),
    target_page_type: str = Form("explanation"),
    db: Session = Depends(dependencies.get_db_dep),
    user=Depends(dependencies.get_current_user),
):
    manager = KeywordManager(db)
    manager.create(
        phrase,
        priority_score=priority_score,
        search_intent=search_intent,
        target_page_type=target_page_type,
    )
    return RedirectResponse(url="/admin/keywords", status_code=303)


@router.post("/keywords/{keyword_id}/queue")
def queue_keyword(keyword_id: int, db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    manager = KeywordManager(db)
    manager.queue_keywords([keyword_id])
    return RedirectResponse("/admin/keywords", 303)


@router.post("/keywords/import")
def import_keywords(csv_text: str = Form(...), db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    manager = KeywordManager(db)
    manager.import_csv(csv_text)
    return RedirectResponse("/admin/keywords", 303)


@router.get("/pages", response_class=HTMLResponse)
def admin_pages(request: Request, db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    pages = db.query(Page).order_by(Page.updated_at.desc()).limit(100).all()
    return templates.TemplateResponse("admin/pages.html", {"request": request, "pages": pages, "user": user})


@router.get("/pages/{page_id}", response_class=HTMLResponse)
def edit_page(page_id: int, request: Request, db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("admin/page_edit.html", {"request": request, "page": page, "user": user})


@router.post("/pages/{page_id}/publish")
def publish_page_action(page_id: int, db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404)
    page.status = PageStatus.PUBLISHED
    page.published_at = page.published_at or page.updated_at
    db.commit()
    rebuild_sitemap_cache(db)
    return RedirectResponse(f"/admin/pages/{page_id}", 303)


@router.post("/pages/{page_id}/regenerate")
def regenerate_page(page_id: int, db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page or not page.keyword_id:
        raise HTTPException(status_code=404)
    engine = ContentEngine(db)
    engine.generate_page(page.keyword, force=True)
    return RedirectResponse(f"/admin/pages/{page_id}", 303)


@router.post("/generate/{keyword_id}")
def manual_generate(keyword_id: int, db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404)
    engine = ContentEngine(db)
    engine.generate_page(keyword)
    return RedirectResponse("/admin/keywords", 303)


@router.post("/publish-now")
def publish_now(db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    publish_ready_pages(db, limit=5, dry_run=False)
    rebuild_sitemap_cache(db)
    return RedirectResponse("/admin", 303)


@router.get("/settings", response_class=HTMLResponse)
def settings_view(request: Request, db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    service = SettingsService(db)
    context = {
        "request": request,
        "ads_top": service.get("ads_top_code", ""),
        "ads_mid": service.get("ads_mid_code", ""),
        "ads_bottom": service.get("ads_bottom_code", ""),
        "affiliate": service.get("affiliate_block_html", ""),
        "analytics": service.get("analytics_snippet", ""),
        "daily_generation_quota": service.get("daily_generation_quota", "5"),
        "daily_publish_quota": service.get("daily_publish_quota", "5"),
        "user": user,
    }
    return templates.TemplateResponse("admin/settings.html", context)


@router.post("/settings")
def save_settings(
    request: Request,
    ads_top: str = Form(""),
    ads_mid: str = Form(""),
    ads_bottom: str = Form(""),
    affiliate: str = Form(""),
    analytics: str = Form(""),
    daily_generation_quota: int = Form(5),
    daily_publish_quota: int = Form(5),
    db: Session = Depends(dependencies.get_db_dep),
    user=Depends(dependencies.get_current_user),
):
    SettingsService(db).bulk_set(
        {
            "ads_top_code": ads_top,
            "ads_mid_code": ads_mid,
            "ads_bottom_code": ads_bottom,
            "affiliate_block_html": affiliate,
            "analytics_snippet": analytics,
            "daily_generation_quota": daily_generation_quota,
            "daily_publish_quota": daily_publish_quota,
        }
    )
    return RedirectResponse("/admin/settings", 303)
