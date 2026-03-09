from core.templates import templates
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from infraestructure.database.repositories.fighters_repository import FighterRepository
from schemas.fighters import FighterForm, FighterRead, FighterUpdate
from services.fighters import (
    create_fighter_service,
    create_fighter_with_features_service,
    delete_fighter_service,
    get_all_fighters_service,
    get_fighter_by_id_service,
    get_fighter_update_form,
    update_fighter_service,
)

from .injection import get_fighter_repository

router = APIRouter(prefix="/fighters", tags=["Fighters"])

fighter_repo_dep = Depends(get_fighter_repository)
fighter_update_form_dep = Depends(get_fighter_update_form)


@router.get("/", name="list_fighters", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def get_all_fighters(request: Request, repo: FighterRepository = fighter_repo_dep):
    try:
        fighters = get_all_fighters_service(repo)
        return templates.TemplateResponse("fighters/list.html", {"request": request, "fighters": fighters})

    except ValueError:
        return templates.TemplateResponse("fighters/not_found.html", {"request": request})


@router.get("/{id}/details", name="get_fighter", response_model=FighterRead, status_code=status.HTTP_200_OK)
def get_fighter(request: Request, id: int, repo: FighterRepository = fighter_repo_dep):
    fighter = get_fighter_by_id_service(id, repo)
    if not fighter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fighter not found")
    return templates.TemplateResponse("fighters/get.html", {"request": request, "fighter": fighter})


# template form to create
@router.get("/create_fighter_view", name="create_fighter_form", response_class=HTMLResponse)
def create_fighter_form(request: Request):
    return templates.TemplateResponse("fighters/create.html", {"request": request})


# template form to update
@router.get("{id}/update", name="update_fighter_form", response_class=HTMLResponse)
def update_fighter_form(request: Request, id: int, repo: FighterRepository = fighter_repo_dep):
    fighter = get_fighter_by_id_service(id, repo)
    if not fighter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fighter not found")
    return templates.TemplateResponse("fighters/update.html", {"request": request, "fighter": fighter})


@router.post("/", name="create_fighter", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def create_fighter(request: Request, form_data: FighterForm = fighter_repo_dep, repo: FighterRepository = fighter_repo_dep):
    fighter = create_fighter_service(form_data, repo)
    if not fighter:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="error creating fighter")
    return RedirectResponse(url=request.url_for("list_fighters"), status_code=status.HTTP_303_SEE_OTHER)


# we need to use put as post because the template
@router.post("/{id}/update", name="update_fighter", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def update_fighter(request: Request, id: int, form_data: FighterUpdate = fighter_update_form_dep, repo: FighterRepository = fighter_repo_dep):
    fighter = update_fighter_service(id, form_data, repo)
    if not fighter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fighter not found")
    return RedirectResponse(url=request.url_for("get_fighter", id=id), status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/{id}", name="delete_fighter", status_code=status.HTTP_200_OK)
def delete_fighter(request: Request, id: int, repo: FighterRepository = fighter_repo_dep):
    delete_fighter_service(id, repo)
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = str(request.url_for("list_fighters"))
    return response


@router.post("/features")
async def create_features_fighter(form_data: FighterForm, repo: FighterRepository = fighter_repo_dep):
    return await create_fighter_with_features_service(form_data, repo)
