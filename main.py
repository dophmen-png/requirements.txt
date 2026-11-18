from fastapi import FastAPI

app = FastAPI(title="FastAPI Render Free", version="1.0.0")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "FastAPI is running", "health": "/health"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
