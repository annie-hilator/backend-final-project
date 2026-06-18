from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.models import Candidate, Category, Resume, User
from app.schemas.schemas import (
    CandidateCreate,
    CandidateResponse,
    ResumeCreate,
    ResumeResponse,
    ResumeUpdate,
)

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/candidates/", response_model=CandidateResponse)
def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_candidate = Candidate(**candidate.model_dump())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


@router.get("/candidates/", response_model=list[CandidateResponse])
def get_candidates(db: Session = Depends(get_db)):
    return db.query(Candidate).all()

@router.post("/", response_model=ResumeResponse)
def create_resume(resume: ResumeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    candidate = db.query(Candidate).filter(
        Candidate.id == resume.candidate_id
    ).first()

    category = db.query(Category).filter(
        Category.id == resume.category_id
    ).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    resume_data = resume.model_dump()
    resume_data["created_by_user_id"] = current_user.id

    db_resume = Resume(**resume_data)

    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    return db_resume


@router.get("/", response_model=list[ResumeResponse])
def get_resumes(
    status: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Resume).filter(Resume.is_deleted == False)

    if status:
        query = query.filter(Resume.status == status)

    if category_id:
        query = query.filter(Resume.category_id == category_id)

    return query.all()


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resume


@router.patch("/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    update_data = resume_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(resume, key, value)

    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume.is_deleted = True
    db.commit()
    db.refresh(resume)

    return {"message": "Resume marked as deleted"}