from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Application, Resume, User, Vacancy
from app.routers.auth import get_current_user
from app.schemas.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    VacancyStatisticsResponse,
)

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/", response_model=ApplicationResponse)
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == application.vacancy_id,
        Vacancy.is_deleted == False,
    ).first()

    resume = db.query(Resume).filter(
        Resume.id == application.resume_id,
        Resume.is_deleted == False,
    ).first()

    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not vacancy.is_open:
        raise HTTPException(status_code=400, detail="Vacancy is closed")

    db_application = Application(**application.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application


@router.get("/", response_model=list[ApplicationResponse])
def get_applications(
    vacancy_id: int | None = None,
    resume_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Application).filter(Application.is_deleted == False)

    if vacancy_id:
        query = query.filter(Application.vacancy_id == vacancy_id)

    if resume_id:
        query = query.filter(Application.resume_id == resume_id)

    if status:
        query = query.filter(Application.status == status)

    return query.all()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.is_deleted == False,
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    application_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.is_deleted == False,
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = application_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(application, key, value)

    db.commit()
    db.refresh(application)

    return application


@router.delete("/{application_id}")
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.is_deleted = True
    db.commit()
    db.refresh(application)

    return {"message": "Application marked as deleted"}


@router.get("/statistics/vacancy/{vacancy_id}", response_model=VacancyStatisticsResponse)
def get_vacancy_statistics(vacancy_id: int, db: Session = Depends(get_db)):
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.is_deleted == False,
    ).first()

    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    applications = db.query(Application).filter(
        Application.vacancy_id == vacancy_id,
        Application.is_deleted == False,
    ).all()

    return VacancyStatisticsResponse(
        vacancy_id=vacancy_id,
        total_applications=len(applications),
        new_applications=len([a for a in applications if a.status == "new"]),
        interview_applications=len([a for a in applications if a.status == "interview"]),
        rejected_applications=len([a for a in applications if a.status == "rejected"]),
        accepted_applications=len([a for a in applications if a.status == "accepted"]),
    )