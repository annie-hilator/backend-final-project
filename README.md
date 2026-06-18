# HR Service

Backend-сервис для HR-отдела, позволяющий работать с вакансиями, кандидатами, резюме и откликами на вакансии.

## Стек технологий

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- Pytest
- Docker
- Docker Compose
- Uvicorn

## Основной функционал

- регистрация пользователей;
- аутентификация пользователей;
- выход из системы;
- смена пароля;
- обновление токена;
- создание, получение, изменение и удаление вакансий;
- фильтрация вакансий по статусу открытия, категории и должности;
- закрытие вакансии;
- создание, получение, изменение и удаление резюме;
- создание и получение кандидатов;
- создание и обработка откликов на вакансии;
- статистика по кандидатам на вакансию;
- soft delete для вакансий, резюме и откликов.

## Модель данных

В проекте используются следующие сущности:

- User - пользователь системы;
- Category - профессиональная категория;
- Position - должность;
- Vacancy - вакансия;
- Candidate - кандидат;
- Resume - резюме кандидата;
- Application - отклик на вакансию.

Связи между сущностями:

- Category 1:N Vacancy;
- Position 1:N Vacancy;
- Category 1:N Resume;
- Candidate 1:N Resume;
- Vacancy 1:N Application;
- Resume 1:N Application.

Модель данных приведена к третьей нормальной форме: справочники вынесены в отдельные таблицы, данные кандидатов не дублируются в резюме, связи реализованы через внешние ключи.

Вакансии, резюме и отклики не удаляются физически из базы данных.  
При удалении поле `is_deleted` меняется на `true`.

## Запуск через Docker Compose

```
docker compose up --build
```

После запуска приложение будет доступно по адресу:

```text
http://localhost:8000/docs
```

## Тесты

Запуск тестов:

```bash
pytest
```

## Основные эндпоинты

### Auth

* `POST /auth/register` - регистрация;
* `POST /auth/login` - вход;
* `POST /auth/logout` - выход;
* `POST /auth/change-password` - смена пароля;
* `POST /auth/refresh-token` - обновление токена.

### Categories

* `POST /categories/` - создать категорию;
* `GET /categories/` - получить категории.

### Positions

* `POST /positions/` - создать должность;
* `GET /positions/` - получить должности.

### Vacancies

* `POST /vacancies/` - создать вакансию;
* `GET /vacancies/` - получить вакансии;
* `GET /vacancies/{vacancy_id}` - получить вакансию по id;
* `PATCH /vacancies/{vacancy_id}` - изменить вакансию;
* `PATCH /vacancies/{vacancy_id}/close` - закрыть вакансию;
* `DELETE /vacancies/{vacancy_id}` - отметка вакансии как удалённой.

### Candidates and Resumes

* `POST /resumes/candidates/` - создать кандидата;
* `GET /resumes/candidates/` - получить кандидатов;
* `POST /resumes/` - создать резюме;
* `GET /resumes/` - получить резюме;
* `GET /resumes/{resume_id}` - получить резюме по id;
* `PATCH /resumes/{resume_id}` - изменить резюме;
* `DELETE /resumes/{resume_id}` - отметка резюме как удалённого.

### Applications

* `POST /applications/` - создать отклик;
* `GET /applications/` - получить отклики;
* `GET /applications/{application_id}` - получить отклик по id;
* `PATCH /applications/{application_id}` - изменить статус отклика;
* `DELETE /applications/{application_id}` - отметка отклика как удалённого;
* `GET /applications/statistics/vacancy/{vacancy_id}` - статистика по кандидатам на вакансию.

## Тесты

Запуск тестов:

```
pytest
```
Запуск тестов с покрытием:

```
pytest --cov=app --cov-report=term-missing
```

Текущее покрытие тестами: **94%**.