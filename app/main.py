from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .core import load

config = load()

app = FastAPI(
    title="HH Auto Apply API",
    version="1.0.0",
)

# CORS (если нужен фронтенд)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.environment.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "HH Auto Apply API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["root"])
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.environment.debug,
        log_level=config.environment.log_level.lower(),
    )
