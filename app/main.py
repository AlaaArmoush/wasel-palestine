from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from app.api.v1.router import api_router
from app.utils.responses import APIResponse

app = FastAPI(
    title="Wasel Palestine API",
    description="Smart Mobility & Checkpoint Intelligence Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "success": False,
                "message": "Validation error",
                "data": exc.errors(),
            }
        ),
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "message": "Resource not found", "data": None},
    )


app.include_router(api_router, prefix="/api/v1")


class HealthData(BaseModel):
    version: str


@app.get("/health", response_model=APIResponse[HealthData], tags=["Health"])
def health_check():
    return {"success": True, "message": "ok", "data": {"version": "1.0.0"}}

