from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import doctors, health, patients, workers
from app.core.errors import ApiError


class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"


app = FastAPI(
    title="Hospital Directory Read API",
    version="1.1.0",
    description="Read-only internal API for patients, doctors, and workers. "
    "Used by HCAT and HCopilot.",
    openapi_url="/api/directory/v1/openapi.json",
    docs_url="/api/directory/v1/docs",
    redoc_url="/api/directory/v1/redoc",
    default_response_class=UTF8JSONResponse,
)

API_PREFIX = "/api/directory/v1"

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(patients.router, prefix=API_PREFIX)
app.include_router(doctors.router, prefix=API_PREFIX)
app.include_router(workers.router, prefix=API_PREFIX)


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> UTF8JSONResponse:
    return UTF8JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "message": exc.message},
    )


_HTTP_STATUS_ERROR_CODES = {
    status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> UTF8JSONResponse:
    error_code = _HTTP_STATUS_ERROR_CODES.get(exc.status_code, "ERROR")
    message = exc.detail if isinstance(exc.detail, str) else "Request could not be processed"
    return UTF8JSONResponse(
        status_code=exc.status_code,
        content={"error": error_code, "message": message},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> UTF8JSONResponse:
    return UTF8JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "VALIDATION_ERROR", "message": "Invalid parameter values"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> UTF8JSONResponse:
    return UTF8JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "SERVER_ERROR", "message": "An unexpected error occurred"},
    )
