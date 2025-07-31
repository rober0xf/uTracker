from http import HTTPStatus

import requests
from fastapi.exceptions import HTTPException

from app.db.settings import settings_api


def get_external_fighter_features(name: str):
    api_key = settings_api.rapidapi_api_key
    if not api_key:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="api key is not set")

    url = "https://mma-stats.p.rapidapi.com/search"
    querystring = {"name": name}
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": "mma-stats.p.rapidapi.com"}

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
    except requests.RequestException:
        raise HTTPException(status_code=HTTPStatus.BAD_GATEWAY, detail="error while fetching external api request") from None

    if response.status_code != HTTPStatus.OK:
        raise HTTPException(status_code=HTTPStatus.BAD_GATEWAY, detail=f"external api error. status: {response.status_code}")

    try:
        data = response.json()
    except ValueError:
        raise HTTPException(status_code=HTTPStatus.BAD_GATEWAY, detail="invalid json response from external api") from None

    if not isinstance(data, list) or not data:  # the api response is in a list
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="fighter not found from the external api")

    return data[0]  # first appearance
