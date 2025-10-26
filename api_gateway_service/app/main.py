# pylint:disable=:redefined-outer-name
# import time
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(lifespan=lifespan)


# @app.middleware("http")
# async def log_request(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     formatted_process_time = f"{process_time:.2f}"

#     logger.info(
#         f"request_path={request.url.path} "
#         f"method={request.method} "
#         f"status_code={response.status_code} "
#         f"process_time_ms={formatted_process_time}"
#     )
#     return response


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(request: Request, path: str):
    """Эта функция определяет, какому сервису перенаправить запрос,
    основываясь на начальной части URL-пути."""
    target_url = None

    if path.startswith("users"):
        target_url = f"{AUTH_SERVICE_URL}/{path}"
    elif path.startswith("tasks"):
        target_url = f"{TASK_SERVICE_URL}/{path}"

    if not target_url:
        return Response(content="Not Found", status_code=404)

    body = await request.body()

    proxied_req = app.state.http_client.build_request(
        method=request.method,
        url=target_url,
        headers=request.headers,
        params=request.query_params,
        content=body,
    )

    response = await app.state.http_client.send(proxied_req)

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )
