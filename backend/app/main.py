from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # для пропуска запросов с фронта на api

from app.database import Base, engine # Base содержит все модели, которые мы описали, engine - подключение к SQLite файлу
from app.api import accounts, categories, transactions # регистрируем роутеры

Base.metadata.create_all(bind=engine) # в классе Base хранятся метаданные всех таблиц приложения, которые должны быть созданы на БД budget.db

app = FastAPI(title="Family Budget API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
) # для пропуска запросов с фронта на api. CORS-это политика безопасности браузера

app.include_router(accounts.router) # Регистрируем все роутеры в приложении
app.include_router(categories.router)
app.include_router(transactions.router)

@app.get('/health') # Простой эндпоинт для проверки, что сервер живой
def health()->dict:
    return {'status': 'ok'}
