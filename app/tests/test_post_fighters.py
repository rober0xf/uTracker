from unittest import mock
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.db.models import FightersDB


def test_post_fighter_mock(client: TestClient):
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
        "created_at": "2025-08-06T15:42:30.617366",
        "updated_at": None,
        **mock_fighter,
    }

    with patch("app.routes.fighters.create_fighter_service") as mock_service:
        mock_service.return_value = mock_created_fighter
        response = client.post("/fighters/", data=mock_fighter)
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["name"] == mock_fighter["name"]
        assert response_data["division"] == mock_fighter["division"]
        assert response_data["wins"] == mock_fighter["wins"]
        assert response_data["losses"] == mock_fighter["losses"]
        assert response_data["height"] == mock_fighter["height"]
        assert response_data["weight"] == mock_fighter["weight"]
        assert response_data["reach"] == mock_fighter["reach"]

        # Test timestamp fields exist
        assert "created_at" in response_data
        assert "updated_at" in response_data
        assert response.status_code == 201
        assert response.json() == mock_created_fighter
        mock_service.assert_called_once_with(
            name="Jon Jones",
            division="heavyweight",
            birth_date="1987-07-19",
            wins=28,
            losses=1,
            draws=0,
            no_contest=0,
            height=1.93,
            weight=107.0,
            reach="215.0",  # Keep as int if that's what you're sending
            db=mock.ANY,  # Match any database session object
        )


# test post request without database verification. response only verification
def test_post_fighter_integration(client: TestClient):
    mock_fighter = {
        "name": "Ilia Topuria",
        "division": "lightweight",
        "birth_date": "1997-01-21",
        "wins": 16,
        "losses": 0,
        "draws": 0,
        "no_contest": 0,
        "height": 1.7,
        "weight": 66.0,
        "reach": 175,
    }

    response = client.post("/fighters/", data=mock_fighter)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == mock_fighter["name"]
    assert "id" in data


# test post with database integration
def test_post_fighter(client: TestClient, db_session):
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

    # simple check if existing
    existing_fighter = db_session.query(FightersDB).filter_by(name="Bo Nickal").first()
    assert existing_fighter is None

    response = client.post("/fighters/", data=fighter_data)
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["name"] == fighter_data["name"]
    assert response_data["height"] == fighter_data["height"]
    assert "id" in response_data

    created_fighter = db_session.query(FightersDB).filter_by(name="Bo Nickal").first()
    assert created_fighter is not None
    assert created_fighter.division == fighter_data["division"]
    assert response_data["id"] == created_fighter.id


# TODO: three test implementation
