from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze_routes import router as analyze_router

app = FastAPI(
    title="Deepfake Detection API",
    description="Backend API za otkrivanje deepfake slika i videa",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/")
def root():
    return {
        "message": "Deepfake Detection API radi"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }