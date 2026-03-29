from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import dependencies
from app.models import Keyword
from app.services.keyword_manager import KeywordManager

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/keywords/export")
def export_keywords(db: Session = Depends(dependencies.get_db_dep), user=Depends(dependencies.get_current_user)):
    manager = KeywordManager(db)
    csv_text = manager.export_csv(db.query(Keyword).limit(1000).all())
    return JSONResponse(content={"csv": csv_text})
