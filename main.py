
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db.models import Base
from app.db.session import engine
from app.db.settings import settings_api
from app.routes.cards import router as cards_router
from app.routes.fighters import router as fighters_router
from app.routes.fights import router as fights_router
from app.routes.picks import router as picks_router

RAPIDAPI_API_KEY = settings_api.rapidapi_api_key
if not RAPIDAPI_API_KEY:
    raise RuntimeError("RAPIDAPI_API_KEY is not set")

with engine.connect() as conn:
    print("connected to database:", conn)

# create the tables
Base.metadata.create_all(bind=engine)

# server instances & html rendering
app = FastAPI(title="uTracker")
templates = Jinja2Templates(directory="templates")

app.include_router(fights_router)
app.include_router(fighters_router)
app.include_router(cards_router)
app.include_router(picks_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


if __name__ == "__main__":
    port = 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
