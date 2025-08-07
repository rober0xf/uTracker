import httpx

from app.db.settings import settings_api


async def get_external_fighter_features(name: str) -> dict | None:
    api_key = settings_api.rapidapi_api_key
    if not api_key:
        return None

    url = "https://mma-stats.p.rapidapi.com/search"
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": "mma-stats.p.rapidapi.com"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params={"name": name})
            if response.status_code != 200:
                return None

            data = response.json()
            return data[0] if isinstance(data, list) and data else None  # [0] first appearance

    except Exception as e:
        print(f"error fetching external data for {name}: {str(e)}")
        return None
