from fastapi import FastAPI
from core.database import Base, engine

from model import branch_model
from routes.branch_routes import router as branch_router

# Crear las tablas en la base de datos SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Palmeras en la Mancha Records API",
    version="1.0.0"
)

app.include_router(branch_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "API de Palmeras en la Mancha Records funcionando"}