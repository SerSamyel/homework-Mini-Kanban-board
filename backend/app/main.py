from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import board, tasks

app = FastAPI(
    title="Boardly API",
    version="1.0.0",
    description=(
        "Single-user MVP backend implementing openapi.yaml — no accounts, "
        "no login, no authentication on any endpoint."
    ),
)

# Permissive CORS: fine for local dev where the frontend (static server) and
# this API run on different ports. Tighten this before deploying anywhere.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(board.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")


@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok"}
