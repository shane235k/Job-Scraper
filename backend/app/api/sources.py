from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.source import Source
from app.schemas.source import SourceResponse, SourceListResponse
from app.engine.runner import IngestionRunner, ADAPTER_REGISTRY

router = APIRouter(tags=["Sources"])

@router.get("/sources", response_model=SourceListResponse)
def list_sources(db: Session = Depends(get_db)):
    for adapter in ADAPTER_REGISTRY.values():
        IngestionRunner.ensure_source_record(db, adapter)
        
    sources = db.query(Source).order_by(Source.name.asc()).all()
    return SourceListResponse(items=sources)

@router.get("/sources/{source_id}", response_model=SourceResponse)
def get_source(source_id: str, db: Session = Depends(get_db)):
    adapter = ADAPTER_REGISTRY.get(source_id)
    if adapter:
        IngestionRunner.ensure_source_record(db, adapter)
        
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail=f"Source with ID '{source_id}' not found.")
    return source
