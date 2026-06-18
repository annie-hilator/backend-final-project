from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    token = Column(String(255), nullable=True)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    vacancies = relationship("Vacancy", back_populates="category")
    resumes = relationship("Resume", back_populates="category")


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    vacancies = relationship("Vacancy", back_populates="position")


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    is_open = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)

    category = relationship("Category", back_populates="vacancies")
    position = relationship("Position", back_populates="vacancies")

    applications = relationship("Application", back_populates="vacancy")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50), nullable=False)

    resumes = relationship("Resume", back_populates="candidate")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    experience = Column(Text, nullable=False)
    status = Column(String(50), default="new", nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    candidate = relationship("Candidate", back_populates="resumes")

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="resumes")

    applications = relationship("Application", back_populates="resume")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), default="new", nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    vacancy = relationship("Vacancy", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")