from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.artist_routes import router as artist_router
from routes.album_format_routes import router as album_format_router
from routes.format_routes import router as format_router
from routes.record_labels_routes import router as record_label_router
from routes.branch_routes import router as branch_router
from routes.album_routes import router as album_router

app = FastAPI(
    title="Palmeras en la Mancha Records API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(branch_router)
app.include_router(album_router)
app.include_router(album_format_router)
app.include_router(artist_router)
app.include_router(record_label_router)
app.include_router(format_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "API de Palmeras en la Mancha Records funcionando"}