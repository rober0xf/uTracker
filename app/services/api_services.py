import httpx

from app.db.settings import settings_api

_fighter_cache: dict[str, dict] = {}


async def get_external_fighter_features(name: str) -> dict | None:
    # only get if it wasnt called before
    if name in _fighter_cache:
        return _fighter_cache[name]

    api_key = settings_api.rapidapi_api_key
    if not api_key:
        return None

    url = "https://mma-stats.p.rapidapi.com/search"
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": "mma-stats.p.rapidapi.com"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            print(f"Fetching data for: {name}")
            response = await client.get(url, headers=headers, params={"name": name})
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")  # debug
            if response.status_code != 200:
                return None

            data = response.json()
            fighter = data[0] if isinstance(data, list) and data else None  # [0] first appearance
            if fighter:
                _fighter_cache[name] = fighter
            return fighter

    except Exception as e:
        print(f"error fetching external data for {name}: {str(e)}")
        return None
