import json
from pathlib import Path

from fast_flights import Flight

from src.analysis import get_average_cost
from src.flights import ParsedFlight


def load_flights_from_json(filename: str) -> list[ParsedFlight]:
    file_path = Path.cwd() / "tests" / "data" / filename
    with file_path.open("r") as f:
        data = json.load(f)
    return [ParsedFlight(**item) for item in data]


def test_get_average_price():
    flights = load_flights_from_json("one_way_flights.json")
    result = get_average_cost(flights)
    assert result >= 0
