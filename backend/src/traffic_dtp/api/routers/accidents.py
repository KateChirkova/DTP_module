from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.traffic_dtp.api.deps import get_current_user
from src.traffic_dtp.db.models import Accident
from src.traffic_dtp.db.models.user import User
from src.traffic_dtp.db.session import get_db

router = APIRouter(prefix="/api/v1", tags=["accidents"])


@router.get("/accidents")
def get_accidents(
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(
        None,
        pattern=r"^(new|created|updated|resolved|all)?$",
        description="new / created / updated / resolved — фильтр; all или пусто — все ДТП",
    ),
):
    query = db.query(Accident)

    # фильтр по статусу; all/пусто — все ДТП (активные и закрытые)
    if status and status != "all":
        filter_status = "new" if status == "created" else status
        query = query.filter(Accident.event_status == filter_status)

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
                "is_active": a.is_active,
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                "first_seen": a.first_seen.isoformat() if a.first_seen else None,
                "last_seen": a.last_seen.isoformat() if a.last_seen else None,
                "missed_screenshots": a.missed_screenshots,
            }
            for a in accidents
        ],
    }
