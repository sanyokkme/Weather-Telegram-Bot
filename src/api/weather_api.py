import requests
from typing import TypeGuard, TypedDict
from config.bot_configuration import Config


class WeatherCondition(TypedDict):
    text: str
    icon: str
    code: int


class WeatherLocation(TypedDict):
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime_epoch: int
    localtime: str


class WeatherCurrent(TypedDict):
    last_updated_epoch: int
    last_updated: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: WeatherCondition
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    windchill_c: float
    windchill_f: float
    heatindex_c: float
    heatindex_f: float
    dewpoint_c: float
    dewpoint_f: float
    vis_km: float
    vis_miles: float
    uv: float
    gust_mph: float
    gust_kph: float
    short_rad: float | int
    diff_rad: float | int
    dni: float | int
    gti: float | int


class WeatherResponse(TypedDict):
    location: WeatherLocation
    current: WeatherCurrent


def _is_str_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    if not isinstance(value, dict):
        return False

    dict_keys: list[object] = list(value.keys())
    for dict_key in dict_keys:
        if not isinstance(dict_key, str):
            return False

    return True


def _ensure_dict(value: object) -> dict[str, object]:
    if not _is_str_object_dict(value):
        raise TypeError("Expected dictionary response from WeatherAPI")
    return value


def _to_str(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("Expected string value from WeatherAPI")
    return value


def _to_int(value: object) -> int:
    if not isinstance(value, int):
        raise TypeError("Expected integer value from WeatherAPI")
    return value


def _to_float(value: object) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError("Expected numeric value from WeatherAPI")
    return float(value)


def _parse_weather_response(payload: object) -> WeatherResponse:
    data = _ensure_dict(payload)
    location = _ensure_dict(data["location"])
    current = _ensure_dict(data["current"])
    condition = _ensure_dict(current["condition"])

    return {
        "location": {
            "name": _to_str(location["name"]),
            "region": _to_str(location["region"]),
            "country": _to_str(location["country"]),
            "lat": _to_float(location["lat"]),
            "lon": _to_float(location["lon"]),
            "tz_id": _to_str(location["tz_id"]),
            "localtime_epoch": _to_int(location["localtime_epoch"]),
            "localtime": _to_str(location["localtime"]),
        },
        "current": {
            "last_updated_epoch": _to_int(current["last_updated_epoch"]),
            "last_updated": _to_str(current["last_updated"]),
            "temp_c": _to_float(current["temp_c"]),
            "temp_f": _to_float(current["temp_f"]),
            "is_day": _to_int(current["is_day"]),
            "condition": {
                "text": _to_str(condition["text"]),
                "icon": _to_str(condition["icon"]),
                "code": _to_int(condition["code"]),
            },
            "wind_mph": _to_float(current["wind_mph"]),
            "wind_kph": _to_float(current["wind_kph"]),
            "wind_degree": _to_int(current["wind_degree"]),
            "wind_dir": _to_str(current["wind_dir"]),
            "pressure_mb": _to_float(current["pressure_mb"]),
            "pressure_in": _to_float(current["pressure_in"]),
            "precip_mm": _to_float(current["precip_mm"]),
            "precip_in": _to_float(current["precip_in"]),
            "humidity": _to_int(current["humidity"]),
            "cloud": _to_int(current["cloud"]),
            "feelslike_c": _to_float(current["feelslike_c"]),
            "feelslike_f": _to_float(current["feelslike_f"]),
            "windchill_c": _to_float(current["windchill_c"]),
            "windchill_f": _to_float(current["windchill_f"]),
            "heatindex_c": _to_float(current["heatindex_c"]),
            "heatindex_f": _to_float(current["heatindex_f"]),
            "dewpoint_c": _to_float(current["dewpoint_c"]),
            "dewpoint_f": _to_float(current["dewpoint_f"]),
            "vis_km": _to_float(current["vis_km"]),
            "vis_miles": _to_float(current["vis_miles"]),
            "uv": _to_float(current["uv"]),
            "gust_mph": _to_float(current["gust_mph"]),
            "gust_kph": _to_float(current["gust_kph"]),
            "short_rad": _to_float(current["short_rad"]),
            "diff_rad": _to_float(current["diff_rad"]),
            "dni": _to_float(current["dni"]),
            "gti": _to_float(current["gti"]),
        },
    }


def get_weather(location: str) -> WeatherResponse:
    url = f"http://api.weatherapi.com/v1/current.json?key={Config.WEATHER_API_KEY}&q={location}&lang=en"

    response = requests.get(url)
    response.raise_for_status()
    return _parse_weather_response(response.json())


def get_weather_by_coordinates(lat: float, lon: float) -> WeatherResponse:
    url = f"http://api.weatherapi.com/v1/current.json?key={Config.WEATHER_API_KEY}&q={lat},{lon}&lang=en"

    response = requests.get(url)
    response.raise_for_status()
    return _parse_weather_response(response.json())
