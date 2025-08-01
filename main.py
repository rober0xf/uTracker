import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db.models import Base
from app.db.session import engine
from app.routes.cards import router as cards_router
from app.routes.fighters import router as fighters_router
from app.routes.fights import router as fights_router
from app.routes.picks import router as picks_router

load_dotenv()
RAPIDAPI_API_KEY = os.environ.get("RAPIDAPI_API_KEY")
if not RAPIDAPI_API_KEY:
    raise RuntimeError("RAPIDAPI_API_KEY is not set")

# create the tables
Base.metadata.create_all(bind=engine)

# server instances & html rendering
app = FastAPI(title="uTracker API", description="API for tracking UFC fights", version="0.1.0")
templates = Jinja2Templates(directory="templates")


app.include_router(fights_router)
app.include_router(fighters_router)
app.include_router(cards_router)
app.include_router(picks_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    # For development purposes
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
