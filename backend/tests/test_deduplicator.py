import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.engine.normalizer import DataNormalizer
from app.engine.deduplicator import Deduplicator, DeduplicationResult

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_deduplicator_new_updated_duplicate(db_session):
    raw_job = {
        "source_job_id": "101",
        "title": "Backend Lead",
        "company": "Python Co",
        "location": "Remote",
        "description": "Initial description",
        "job_url": "https://python.org/jobs/101/"
    }
    normalized = DataNormalizer.normalize_job(raw_job, "python_org")

    # 1. First insertion -> NEW
    res1, job1 = Deduplicator.process_job(db_session, normalized)
    assert res1 == DeduplicationResult.NEW
    assert job1.title == "Backend Lead"

    # 2. Identical insertion -> DUPLICATE
    res2, job2 = Deduplicator.process_job(db_session, normalized)
    assert res2 == DeduplicationResult.DUPLICATE
    assert job2.id == job1.id

    # 3. Insertion with updated title -> UPDATED
    raw_updated = dict(raw_job)
    raw_updated["title"] = "Senior Backend Lead"
    norm_updated = DataNormalizer.normalize_job(raw_updated, "python_org")
    res3, job3 = Deduplicator.process_job(db_session, norm_updated)
    assert res3 == DeduplicationResult.UPDATED
    assert job3.title == "Senior Backend Lead"
    assert job3.id == job1.id
