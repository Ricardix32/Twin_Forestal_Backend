from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all tables are created
    Base.metadata.create_all(bind=engine)
    try:
        from app.core.database import SessionLocal
        from app.models.region import Region
        db = SessionLocal()
        try:
            if db.query(Region).count() == 0:
                import logging
                logging.getLogger("uvicorn").info("SilvaTwin database is empty. Running initial seed...")
                from seed_data import seed
                seed()
        finally:
            db.close()
    except Exception as e:
        import logging
        logging.getLogger("uvicorn").warning(f"Auto-seed check: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend científico y API de servicios para SilvaTwin - Gemelo Digital Forestal",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": engine.url.drivername,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
