from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.schemas.fighters import Fighters

""" unit test"""


def test_fighter_mock(client: TestClient):
    mock_fighter = {
        "name": "Jon Jones",
        "division": "heavyweight",
        "birth_date": "1987-07-19",
        "wins": 28,
        "losses": 1,
        "draws": 0,
        "no_contest": 0,
        "height": 1.93,
        "weight": 107.0,
        "reach": 215.0,
    }
    mock_created_fighter = {
        "id": 1,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        **mock_fighter,
    }

    with patch("app.routes.fighters.create_fighter_service") as mock_service:
        mock_service.return_value = mock_created_fighter
        response = client.post("/fighters/", data=mock_fighter)
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["name"] == mock_fighter["name"]
        assert response_data["reach"] == mock_fighter["reach"]

        assert "created_at" in response_data
        assert "updated_at" in response_data
        assert response.status_code == 201
        assert response.json() == mock_created_fighter
        mock_service.assert_called_once()


""" integration test"""


def test_full_fields(client: TestClient):
    fighter_data = {
        "name": "Bo Nickal",
        "division": "middleweight",
        "birth_date": "1996-01-14",
        "wins": 7,
        "losses": 1,
        "draws": 0,
        "no_contest": 0,
        "height": 1.85,
        "weight": 83.0,
        "reach": 193,
    }

    response = client.post("/fighters/", data=fighter_data)
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["name"] == fighter_data["name"]
    assert response_data["height"] == fighter_data["height"]
    assert "id" in response_data
    assert "created_at" in response_data
    assert "updated_at" in response_data
    Fighters(**response_data)


# missing field wins
def test_missing_fields(client: TestClient, db_session):
    fighter_data = {
        "name": "Bo Nickal",
        "division": "middleweight",
        "birth_date": "1996-01-14",
        "losses": 1,
        "draws": 0,
        "no_contest": 0,
        "height": 1.85,
        "weight": 83.0,
    }

    response = client.post("/fighters/", data=fighter_data)
    assert response.status_code == 422


def test_empty_fields(client: TestClient):
    fighter_data = {
        "name": "",
    }

    response = client.post("/fighters/", data=fighter_data)
    assert response.status_code == 422
