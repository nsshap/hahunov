import aiohttp

HEADERS = {"User-Agent": "VarvaraCongratsBot/1.0"}


async def geocode_city(city_name: str) -> tuple[float, float] | None:
    """Текстовое название города → (lat, lng)"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "limit": 1}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=HEADERS) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])
    return None


async def reverse_geocode(lat: float, lng: float) -> str:
    """(lat, lng) → читаемое название города"""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lng, "format": "json"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=HEADERS) as resp:
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
                return f"{city}, {country}".strip(", ")
    return "Неизвестно"
