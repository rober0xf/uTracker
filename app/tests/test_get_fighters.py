from datetime import date, datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.db.models import FightersDB
from app.schemas.fighters import Fighters


# test returning data from database.
def test_get_all_fighters(client: TestClient, db_session):
    mock_fighters = [
        {
            "id": 1,
            "name": "Ilia Topuria",
            "division": "lightweight",
            "birth_date": date(1997, 1, 21),
            "wins": 16,
            "losses": 0,
            "draws": 0,
            "no_contest": 0,
            "height": 1.7,
            "weight": 66.0,
            "reach": 175,
            "created_at": datetime.now(),
        },
        {
            "id": 2,
            "name": "Bo Nickal",
            "division": "middleweight",
            "birth_date": date(1996, 1, 14),
            "wins": 7,
            "losses": 1,
            "draws": 0,
            "no_contest": 0,
            "height": 1.85,
            "weight": 83.0,
            "reach": 193,
            "created_at": datetime.now(),
        },
    ]
    for fighter_data in mock_fighters:
        fighter = FightersDB(**fighter_data)
        db_session.add(fighter)
    db_session.flush()

    response = client.get("/fighters/")
    assert response.status_code == 200

    # validate using the pydantic model
    data = response.json()
    for item in data:
        Fighters(**item)

    # check all mock fighters are present
    expected = [Fighters(**f).model_dump() for f in mock_fighters]
    for f in expected:
        assert any(df["name"] == f["name"] for df in data)


# test returning fighter by id from the database.
def test_get_fighter(client: TestClient, db_session):
    mock_fighter = {
        "id": 69,
        "name": "Khamzat Chimaev",
        "division": "middleweight",
        "birth_date": date(1994, 5, 1),
        "wins": 14,
        "losses": 0,
        "draws": 0,
        "no_contest": 0,
        "height": 1.88,
        "weight": 84,
    }
    fighter = FightersDB(**mock_fighter)
    db_session.add(fighter)
    db_session.flush()

    response = client.get(f"/fighters/{mock_fighter['id']}")
    assert response.status_code == 200

    data = response.json()
    Fighters(**data)  # validate the fighter

    assert data["name"] == mock_fighter["name"]
    assert data["id"] == mock_fighter["id"]


""" unit test"""


# test when there are no fighters. using mock
def test_get_all_fighters_empty(client):
    with patch("app.routes.fighters.get_all_fighters_service") as mock_service:
        mock_service.return_value = []

        response = client.get("/fighters/")

        assert response.status_code == 200
        assert response.json() == []


# test that the mock is called once
def test_get_all_fighters_calls_service(client):
    with patch("app.routes.fighters.get_all_fighters_service") as mock_service:
        mock_service.return_value = []

        client.get("/fighters/")
        mock_service.assert_called_once()


def test_get_fighter_not_found(client):
    response = client.get("/fighters/420")
    assert response.status_code == 404
