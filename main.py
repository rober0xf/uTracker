from app.routes.fighters import router as fighters_router
from app.routes.fights import router as fights_router
from app.routes.cards import router as cards_router
from app.routes.picks import router as picks_router
from app.db.session import engine
from app.db.models import Base
from fastapi import FastAPI
import uvicorn
import os

# create the tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="uTracker API", description="API for tracking UFC fights", version="0.1.0")

app.include_router(fights_router)
app.include_router(fighters_router)
app.include_router(cards_router)
app.include_router(picks_router)


@app.get("/")
def root():
    return {"message": "Welcome to uTracker API!"}


if __name__ == "__main__":
    # For development purposes
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
