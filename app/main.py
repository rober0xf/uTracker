import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.templates import templates
from app.infraestructure.database.models.base_model import Base
from app.infraestructure.database.session import engine
from app.infraestructure.database.settings import settings_api
from app.interfaces.api.cards_router import router as cards_router
from app.interfaces.api.fighters_router import router as fighters_router
from app.interfaces.api.fights_router import router as fights_router

RAPIDAPI_API_KEY = settings_api.rapidapi_api_key
if not RAPIDAPI_API_KEY:
    raise RuntimeError("RAPIDAPI_API_KEY is not set")

with engine.connect() as conn:
    print("connected to database:", conn)

# create the tables
Base.metadata.create_all(bind=engine)

# server instances & html rendering
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fights_router)
app.include_router(fighters_router)
app.include_router(cards_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "base.html")


if __name__ == "__main__":
    port = 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
