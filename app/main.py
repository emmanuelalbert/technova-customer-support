from fastapi import FastAPI

app = FastAPI(title="TechNova Customer Support")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
