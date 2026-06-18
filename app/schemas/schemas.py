from pydantic import BaseModel, EmailStr
from enum import Enum

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class PositionBase(BaseModel):
    name: str

class PositionCreate(PositionBase):
    pass

class PositionResponse(PositionBase):
    id: int

    class Config:
        from_attributes = True

class VacancyBase(BaseModel):
    title: str
    description: str
    is_open: bool = True
    is_deleted: bool = False
    category_id: int
    position_id: int
    created_by_user_id: int | None = None


class VacancyCreate(VacancyBase):
    pass


class VacancyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_open: bool | None = None
    is_deleted: bool | None = None
    category_id: int | None = None
    position_id: int | None = None
    created_by_user_id: int | None = None


class VacancyResponse(VacancyBase):
    id: int

    class Config:
        from_attributes = True

class CandidateBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: int

    class Config:
        from_attributes = True

class ResumeStatusSchema(str, Enum):
    new = "new"
    interview = "interview"
    rejected = "rejected"
    accepted = "accepted"


class ApplicationStatusSchema(str, Enum):
    new = "new"
    interview = "interview"
    rejected = "rejected"
    accepted = "accepted"

class ResumeBase(BaseModel):
    experience: str
    status: ResumeStatusSchema = ResumeStatusSchema.new
    is_deleted: bool = False
    candidate_id: int
    category_id: int


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    experience: str | None = None
    status: ResumeStatusSchema | None = None
    created_by_user_id: int | None = None
    is_deleted: bool | None = None
    candidate_id: int | None = None
    category_id: int | None = None


class ResumeResponse(ResumeBase):
    id: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True

class ApplicationBase(BaseModel):
    status: ApplicationStatusSchema = ApplicationStatusSchema.new
    is_deleted: bool = False
    vacancy_id: int
    resume_id: int


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: ApplicationStatusSchema | None = None
    is_deleted: bool | None = None
    vacancy_id: int | None = None
    resume_id: int | None = None


class ApplicationResponse(ApplicationBase):
    id: int

    class Config:
        from_attributes = True


class VacancyStatisticsResponse(BaseModel):
    vacancy_id: int
    total_applications: int
    new_applications: int
    interview_applications: int
    rejected_applications: int
    accepted_applications: int

class ChangePasswordRequest(BaseModel):
    user_id: int
    old_password: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    user_id: int

