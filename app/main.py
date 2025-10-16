from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.users import router as user_router

app = FastAPI(
    title="FastAPI user service - сервис аунтификации",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)


@app.get("/")
async def root():
    """Корневой маршрут, подверждающий, что API работает."""
    return {"message": "Добро пожаловать в user service"}
