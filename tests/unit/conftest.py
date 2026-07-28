from datetime import date
from unittest.mock import MagicMock

import pytest

from app.domain.enums.enums import DivisionEnum, RoundsEnum, WinningMethodEnum
from app.infraestructure.database.models.fight_model import FightDB
from app.infraestructure.database.models.fighter_model import FighterDB
from app.infraestructure.database.repositories.cards_repository import CardRepository
from app.infraestructure.database.repositories.fighters_repository import FighterRepository
from app.infraestructure.database.repositories.fights_repository import FightRepository
from app.interfaces.schemas.card import CardCreate
from app.interfaces.schemas.fighters import FighterUpdate
from app.interfaces.schemas.fights import FightForm, FightUpdate


# repositories
class MockFighterRepo(MagicMock):
    create: MagicMock
    get_all: MagicMock
    get_by_id: MagicMock
    update: MagicMock
    update_features: MagicMock
    delete: MagicMock


class MockCardRepo(MagicMock):
    create_form: MagicMock
    create: MagicMock
    get_all: MagicMock
    get_by_id: MagicMock
    delete: MagicMock


class MockFightRepo(MagicMock):
    get_all: MagicMock
    get_by_id: MagicMock
    create: MagicMock
    save: MagicMock
    delete: MagicMock


@pytest.fixture
def mock_card_repo() -> MockCardRepo:
    return MagicMock(spec=CardRepository)


@pytest.fixture
def mock_fighter_repo() -> MockFighterRepo:
    return MagicMock(spec=FighterRepository)


@pytest.fixture
def mock_fight_repo() -> MockFightRepo:
    return MagicMock(spec=FightRepository)


@pytest.fixture
def card_data():
    return CardCreate(
        card_name="Emmett vs Vallejos",
        card_date=date(2026, 3, 14),
        card_number=None,
    )


@pytest.fixture
def fighter_form():
    mock = MagicMock()
    mock.to_fighter_base_data.return_value = FIGHTER_DATA.copy()
    return mock


@pytest.fixture
def fighter_update() -> FighterUpdate:
    return FighterUpdate(name="Jon Jones Updated", wins=30)


@pytest.fixture
def fighter_empty_update() -> FighterUpdate:
    return FighterUpdate()


@pytest.fixture
def fighter_db() -> FighterDB:
    return FighterDB(**FIGHTER_DATA)


@pytest.fixture
def fight_db() -> FightDB:
    return FightDB(**FIGHT_DATA)


@pytest.fixture
def fight_form() -> MagicMock:
    mock = MagicMock(spec=FightForm)
    mock.to_fights_base_data.return_value = FIGHT_DATA.copy()
    mock.red_corner = 1
    mock.blue_corner = 2
    return mock


@pytest.fixture
def fight_update() -> FightUpdate:
    return FightUpdate(method=WinningMethodEnum.KO)


@pytest.fixture
def fight_empty_update() -> FightUpdate:
    return FightUpdate()


# data
FIGHTER_DATA = {
    "name": "Jon Jones",
    "division": DivisionEnum.HEAVYWEIGHT,
    "birth_date": date(1987, 7, 19),
    "wins": 28,
    "losses": 1,
    "draws": None,
    "no_contest": None,
    "height": 1.93,
    "weight": 77.0,
    "reach": 1.85,
}

FIGHT_DATA = {
    "rounds": RoundsEnum.FIVE,
    "division": DivisionEnum.LIGHTWEIGHT,
    "card": 1,
    "red_corner": 1,
    "blue_corner": 2,
    "favorite": "red",
    "winner": "red",
    "fight_date": date(2026, 3, 14),
    "method": None,
    "round_finish": None,
}
