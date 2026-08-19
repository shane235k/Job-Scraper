import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.run import IngestionRun
from app.models.error import IngestionError
from app.schemas.run import IngestionRunResponse, RunListResponse, IngestionErrorResponse
from app.engine.runner import IngestionRunner

router = APIRouter(tags=["Ingestion Runs"])

# Cooldown period in seconds to prevent rapid-click bot detection flags
COOLDOWN_SECONDS = 45

@router.get("/ingestion/runs", response_model=RunListResponse)
def list_runs(
    source_id: Optional[str] = Query(None, description="Filter by source ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(IngestionRun)
    if source_id:
        query = query.filter(IngestionRun.source_id == source_id)

    total = query.count()
    runs = (
        query.order_by(IngestionRun.start_time.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    result_items = []
    for r in runs:
        errs = db.query(IngestionError).filter(IngestionError.run_id == r.id).all()
        err_resps = [IngestionErrorResponse.from_orm(e) for e in errs]
        run_resp = IngestionRunResponse.from_orm(r)
        run_resp.errors = err_resps
        result_items.append(run_resp)

    return RunListResponse(
        items=result_items,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/ingestion/runs/{run_id}", response_model=IngestionRunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run_rec = db.query(IngestionRun).filter(IngestionRun.id == run_id).first()
    if not run_rec:
        raise HTTPException(status_code=404, detail=f"Ingestion run '{run_id}' not found.")
    
    errs = db.query(IngestionError).filter(IngestionError.run_id == run_rec.id).all()
    run_resp = IngestionRunResponse.from_orm(run_rec)
    run_resp.errors = [IngestionErrorResponse.from_orm(e) for e in errs]
    return run_resp

@router.post("/ingestion/run/{source_id}", response_model=IngestionRunResponse)
async def trigger_run(source_id: str, db: Session = Depends(get_db)):
    """
    Manually trigger an ingestion run for a source.
    Enforces a Source Cooldown Lock to prevent rapid-click bot detection.
    """
    last_run = (
        db.query(IngestionRun)
        .filter(IngestionRun.source_id == source_id)
        .order_by(IngestionRun.start_time.desc())
        .first()
    )

    if last_run and last_run.start_time:
        now = datetime.datetime.utcnow()
        elapsed = (now - last_run.start_time).total_seconds()
        if elapsed < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - elapsed)
            raise HTTPException(
                status_code=429,
                detail=f"Source '{source_id}' is cooling down to prevent rapid-click bot detection. Please wait {remaining} seconds before triggering another manual run."
            )

    try:
        run_rec = await IngestionRunner.run(db, source_id)
        errs = db.query(IngestionError).filter(IngestionError.run_id == run_rec.id).all()
        run_resp = IngestionRunResponse.from_orm(run_rec)
        run_resp.errors = [IngestionErrorResponse.from_orm(e) for e in errs]
        return run_resp
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute ingestion run: {e}")
