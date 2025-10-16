from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.api.routers.users import router as user_router

app = FastAPI(
    title="FastAPI user service - сервис аунтификации",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "https://auth-service-v2-rqoi.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)


@app.get("/")
async def read_index():
    # Возвращаем главную HTML страницу
    return FileResponse("index.html")
