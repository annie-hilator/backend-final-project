from fastapi import FastAPI

from app.core.database import Base, engine
from app.models import models
from app.routers import applications, auth, resumes, vacancies

# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HR Service",
    description="Backend-сервис для работы с вакансиями и резюме",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(vacancies.router)
app.include_router(resumes.router)
app.include_router(applications.router)


@app.get("/")
def root():
    return {"message": "HR Service is running"}