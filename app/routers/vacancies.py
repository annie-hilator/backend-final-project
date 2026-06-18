from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.models import Category, Position, User, Vacancy
from app.schemas.schemas import (
    CategoryCreate,
    CategoryResponse,
    PositionCreate,
    PositionResponse,
    VacancyCreate,
    VacancyResponse,
    VacancyUpdate,
)


router = APIRouter(tags=["Vacancies"])


@router.post("/categories/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.post("/positions/", response_model=PositionResponse)
def create_position(position: PositionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_position = Position(name=position.name)
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position


@router.get("/positions/", response_model=list[PositionResponse])
def get_positions(db: Session = Depends(get_db)):
    return db.query(Position).all()


@router.post("/vacancies/", response_model=VacancyResponse)
def create_vacancy(vacancy: VacancyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(Category).filter(Category.id == vacancy.category_id).first()
    position = db.query(Position).filter(Position.id == vacancy.position_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")

    vacancy_data = vacancy.model_dump()
    vacancy_data["created_by_user_id"] = current_user.id

    db_vacancy = Vacancy(**vacancy_data)
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy


@router.get("/vacancies/", response_model=list[VacancyResponse])
def get_vacancies(
    is_open: bool | None = None,
    category_id: int | None = None,
    position_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Vacancy).filter(Vacancy.is_deleted == False)

    if is_open is not None:
        query = query.filter(Vacancy.is_open == is_open)
    if category_id:
        query = query.filter(Vacancy.category_id == category_id)
    if position_id:
        query = query.filter(Vacancy.position_id == position_id)

    return query.all()


@router.get("/vacancies/{vacancy_id}", response_model=VacancyResponse)
def get_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()

    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    return vacancy


@router.patch("/vacancies/{vacancy_id}", response_model=VacancyResponse)
def update_vacancy(
    vacancy_id: int,
    vacancy_data: VacancyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()

    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    update_data = vacancy_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(vacancy, key, value)

    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.patch("/vacancies/{vacancy_id}/close", response_model=VacancyResponse)
def close_vacancy(vacancy_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()

    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    vacancy.is_open = False
    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.delete("/vacancies/{vacancy_id}")
def delete_vacancy(vacancy_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()

    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    vacancy.is_deleted = True
    db.commit()
    db.refresh(vacancy)

    return {"message": "Vacancy marked as deleted"}