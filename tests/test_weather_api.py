import requests
import pytest

from src.api.weather_api import get_weather


@pytest.fixture
def sample_payload() -> dict[str, object]:
    return {
        "location": {
            "name": "Warsaw",
            "region": "",
            "country": "Poland",
            "lat": 52.25,
            "lon": 21.0,
            "tz_id": "Europe/Warsaw",
            "localtime_epoch": 1774375426,
            "localtime": "2026-03-24 19:03",
        },
        "current": {
            "last_updated_epoch": 1774375200,
            "last_updated": "2026-03-24 19:00",
            "temp_c": 11.2,
            "temp_f": 52.2,
            "is_day": 0,
            "condition": {
                "text": "Суцільна хмарність",
                "icon": "//cdn.weatherapi.com/weather/64x64/night/122.png",
                "code": 1009,
            },
            "wind_mph": 4.7,
            "wind_kph": 7.6,
            "wind_degree": 218,
            "wind_dir": "SW",
            "pressure_mb": 1015.0,
            "pressure_in": 29.97,
            "precip_mm": 0.0,
            "precip_in": 0.0,
            "humidity": 43,
            "cloud": 0,
            "feelslike_c": 10.5,
            "feelslike_f": 50.9,
            "windchill_c": 10.8,
            "windchill_f": 51.5,
            "heatindex_c": 11.5,
            "heatindex_f": 52.7,
            "dewpoint_c": 0.7,
            "dewpoint_f": 33.3,
            "vis_km": 10.0,
            "vis_miles": 6.0,
            "uv": 0.0,
            "gust_mph": 8.1,
            "gust_kph": 13.0,
            "short_rad": 0,
            "diff_rad": 0,
            "dni": 0,
            "gti": 0,
        },
    }


class DummyResponse:
    def __init__(self, payload: dict[str, object], status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self) -> dict[str, object]:
        return self._payload


def test_get_weather_returns_expected_structure(monkeypatch: pytest.MonkeyPatch, sample_payload: dict[str, object]) -> None:
    def fake_get(url: str) -> DummyResponse:
        assert "q=Warsaw" in url
        return DummyResponse(sample_payload)

    monkeypatch.setattr(
        "src.api.weather_api.requests.get", fake_get)

    result = get_weather("Warsaw")

    assert result["location"]["name"] == "Warsaw"
    assert result["location"]["country"] == "Poland"
    assert result["current"]["temp_c"] == 11.2
    assert result["current"]["condition"]["code"] == 1009


def test_get_weather_converts_numeric_fields_to_float(monkeypatch: pytest.MonkeyPatch, sample_payload: dict[str, object]) -> None:
    def fake_get(url: str) -> DummyResponse:
        assert isinstance(url, str)
        return DummyResponse(sample_payload)

    monkeypatch.setattr(
        "src.api.weather_api.requests.get",
        fake_get,
    )

    result = get_weather("Warsaw")

    assert isinstance(result["current"]["short_rad"], float)
    assert isinstance(result["current"]["diff_rad"], float)
    assert isinstance(result["current"]["dni"], float)
    assert isinstance(result["current"]["gti"], float)


def test_get_weather_raises_http_error_for_bad_status(monkeypatch: pytest.MonkeyPatch, sample_payload: dict[str, object]) -> None:
    def fake_get(url: str) -> DummyResponse:
        assert isinstance(url, str)
        return DummyResponse(sample_payload, status_code=400)

    monkeypatch.setattr(
        "src.api.weather_api.requests.get",
        fake_get,
    )

    with pytest.raises(requests.HTTPError):
        get_weather("Warsaw")


def test_get_weather_raises_type_error_for_invalid_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str) -> DummyResponse:
        assert isinstance(url, str)
        return DummyResponse({"location": "invalid", "current": {}}, status_code=200)

    monkeypatch.setattr(
        "src.api.weather_api.requests.get",
        fake_get,
    )

    with pytest.raises(TypeError):
        get_weather("Warsaw")
