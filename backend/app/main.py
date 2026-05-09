from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.api import accounts, categories, transactions, analytics, budgets
from app.models.category import Category, CategoryType
from app.models.budget import Budget  # noqa: F401 — нужен чтобы SQLAlchemy создал таблицу

Base.metadata.create_all(bind=engine)

def seed_categories():
    db = SessionLocal()
    if db.query(Category).count() > 0:
        db.close()
        return

    def add(name, type, parent=None):
        c = Category(name=name, type=type, parent_id=parent.id if parent else None)
        db.add(c)
        db.flush()
        return c

    # Доходы — без групп
    add("Зарплата",                        CategoryType.INCOME)
    add("Выполненные работы и услуги",     CategoryType.INCOME)
    add("Пенсии, пособия, стипендии",      CategoryType.INCOME)
    add("Вычеты",                          CategoryType.INCOME)
    add("Коммерческая деятельность",       CategoryType.INCOME)
    add("Подарки",                         CategoryType.INCOME)
    add("Донаты",                          CategoryType.INCOME)
    add("Дивиденды и проценты",            CategoryType.INCOME)
    add("Страховые выплаты",               CategoryType.INCOME)
    add("Доходы от авторских прав",        CategoryType.INCOME)
    add("Аренда имущества",                CategoryType.INCOME)
    add("Реализация имущества",            CategoryType.INCOME)
    add("Криптовалюта и майнинг",          CategoryType.INCOME)
    add("Прочие финансовые активы",        CategoryType.INCOME)

    # Расходы — группы с дочерними
    жильё = add("Расходы на жильё",        CategoryType.EXPENSE)
    add("Ипотека и аренда",                CategoryType.EXPENSE, жильё)
    add("Коммунальные услуги",             CategoryType.EXPENSE, жильё)
    add("Интернет и телефон",              CategoryType.EXPENSE, жильё)
    add("Ремонт и обслуживание",           CategoryType.EXPENSE, жильё)

    питание = add("Питание",               CategoryType.EXPENSE)
    add("Продукты",                        CategoryType.EXPENSE, питание)
    add("Кафе и рестораны",                CategoryType.EXPENSE, питание)
    add("Доставка еды",                    CategoryType.EXPENSE, питание)

    транспорт = add("Транспорт",           CategoryType.EXPENSE)
    add("Общественный транспорт",          CategoryType.EXPENSE, транспорт)
    add("Такси и каршеринг",               CategoryType.EXPENSE, транспорт)
    add("Топливо и обслуживание авто",     CategoryType.EXPENSE, транспорт)
    add("Парковка и штрафы",               CategoryType.EXPENSE, транспорт)

    здоровье = add("Здоровье",             CategoryType.EXPENSE)
    add("Врачи и медицинские услуги",      CategoryType.EXPENSE, здоровье)
    add("Лекарства",                       CategoryType.EXPENSE, здоровье)
    add("Страховка",                       CategoryType.EXPENSE, здоровье)
    add("Спорт и фитнес",                  CategoryType.EXPENSE, здоровье)

    одежда = add("Одежда и личные вещи",   CategoryType.EXPENSE)
    add("Одежда и обувь",                  CategoryType.EXPENSE, одежда)
    add("Уход за собой",                   CategoryType.EXPENSE, одежда)
    add("Аксессуары",                      CategoryType.EXPENSE, одежда)

    образование = add("Образование и развитие", CategoryType.EXPENSE)
    add("Курсы и обучение",                CategoryType.EXPENSE, образование)
    add("Книги и материалы",               CategoryType.EXPENSE, образование)
    add("Подписки профессиональные",       CategoryType.EXPENSE, образование)

    досуг = add("Досуг и развлечения",     CategoryType.EXPENSE)
    add("Кино, театр, концерты",           CategoryType.EXPENSE, досуг)
    add("Хобби",                           CategoryType.EXPENSE, досуг)
    add("Путешествия и отпуск",            CategoryType.EXPENSE, досуг)
    add("Стриминг и игры",                 CategoryType.EXPENSE, досуг)

    семья = add("Семья и дети",            CategoryType.EXPENSE)
    add("Образование детей",               CategoryType.EXPENSE, семья)
    add("Игрушки и товары для детей",      CategoryType.EXPENSE, семья)
    add("Уход за пожилыми родственниками", CategoryType.EXPENSE, семья)
    add("Домашние животные",               CategoryType.EXPENSE, семья)
    add("Няня",                            CategoryType.EXPENSE, семья)
    add("Развивающие секции",              CategoryType.EXPENSE, семья)
    add("Детская одежда",                  CategoryType.EXPENSE, семья)
    add("Детские расходники",              CategoryType.EXPENSE, семья)

    финансы = add("Финансовые обязательства", CategoryType.EXPENSE)
    add("Кредиты и рассрочки",             CategoryType.EXPENSE, финансы)
    add("Налоги",                          CategoryType.EXPENSE, финансы)
    add("Пенсионные накопления",           CategoryType.EXPENSE, финансы)

    подарки = add("Подарки и благотворительность", CategoryType.EXPENSE)
    add("Подарки друзьям и родственникам", CategoryType.EXPENSE, подарки)
    add("Пожертвования",                   CategoryType.EXPENSE, подарки)

    техника = add("Техника и подписки",    CategoryType.EXPENSE)
    add("Гаджеты и электроника",           CategoryType.EXPENSE, техника)
    add("Программное обеспечение",         CategoryType.EXPENSE, техника)
    add("Облачные сервисы",                CategoryType.EXPENSE, техника)
    add("ИИ",                              CategoryType.EXPENSE, техника)
    add("Развлекательные сервисы",         CategoryType.EXPENSE, техника)

    непредвиденные = add("Непредвиденные расходы", CategoryType.EXPENSE)
    add("Аварийный фонд",                  CategoryType.EXPENSE, непредвиденные)
    add("Непредвиденный ремонт",           CategoryType.EXPENSE, непредвиденные)
    add("Прочие разовые расходы",          CategoryType.EXPENSE, непредвиденные)

    db.commit()
    db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_categories()
    yield


app = FastAPI(title="Family Budget API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(budgets.router)

@app.get('/health')
def health() -> dict:
    return {'status': 'ok'}