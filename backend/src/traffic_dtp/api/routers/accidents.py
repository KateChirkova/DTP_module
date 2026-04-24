from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.traffic_dtp.db.session import get_db
from src.traffic_dtp.db.models import Accident

router = APIRouter(prefix="/api", tags=["accidents"])


@router.get("/v1/accidents")
def get_accidents(
        db: Session = Depends(get_db),
        limit: int = Query(10, ge=1, le=100),
        status: Optional[str] = Query(
            None,
            pattern=r"^(created|updated|resolved|all)?$",
            description="created/updated/resolved/all (пустое=all)"
        )
):
    query = db.query(Accident).filter(Accident.is_active == True)

    # фильтр по статусам
    if status != "all":
        query = query.filter(Accident.event_status == status)

    accidents = query.order_by(Accident.last_seen.desc()).limit(limit).all()

    return {
        "success": True,
        "count": len(accidents),
        "status_filter": status,
        "accidents": [
            {
                "id": a.id,
                "confidence": round(a.confidence or 0, 2),
                "bbox": [a.bbox_x1, a.bbox_y1, a.bbox_x2, a.bbox_y2],
                "status": a.event_status,
                "first_seen": a.first_seen.isoformat() if a.first_seen else None,
                "last_seen": a.last_seen.isoformat() if a.last_seen else None,
                "missed_screenshots": a.missed_screenshots,
            }
            for a in accidents
        ],
    }