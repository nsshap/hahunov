import logging

import aiohttp

HEADERS = {"User-Agent": "VarvaraCongratsBot/1.0"}


async def geocode_city(city_name: str) -> tuple[float, float] | None:
    """Текстовое название города → (lat, lng)"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "limit": 1}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data:
                        return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        logging.warning("geocode_city failed for %r: %s", city_name, e)
    return None


async def reverse_geocode(lat: float, lng: float) -> str:
    """(lat, lng) → читаемое название города"""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lng, "format": "json"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    address = data.get("address", {})
                    city = (
                        address.get("city")
                        or address.get("town")
                        or address.get("village")
                        or address.get("county", "")
                    )
                    country = address.get("country", "")
                    result = f"{city}, {country}".strip(", ")
                    return result or "Неизвестно"
    except Exception as e:
        logging.warning("reverse_geocode failed for %s,%s: %s", lat, lng, e)
    return "Неизвестно"
