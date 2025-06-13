import datetime
import json
from dataclasses import asdict
from pathlib import Path

from fast_flights import Flight

from src.calculator import (FlightRequest, get_airport_code,
                            get_direct_flight_duration,
                            get_flights_from_request, parse_currency)

departure_airport = get_airport_code("amsterdam")
arrival_airport = get_airport_code("los angeles")
currency = parse_currency("USD")
family_size = 4


def save_flights_to_json(flights: list[Flight], filename: str):
    data_dir = Path.cwd() / "tests" / "data"
    data_dir.mkdir(exist_ok=True)
    file_path = data_dir / filename

    if not file_path.exists():
        with file_path.open("w") as f:
            json.dump([asdict(flight) for flight in flights], f, indent=2)
        print(f"Saved {len(flights)} flights to {file_path}")
    else:
        print(f"File {file_path} already exists, not overwriting.")


def load_flights_from_json(filename: str) -> list[Flight]:
    file_path = Path.cwd() / "tests" / "data" / filename
    with file_path.open("r") as f:
        data = json.load(f)
    return [Flight(**item) for item in data]


def test_get_direct_flight_duration():
    sample_request = FlightRequest(
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        family_size=family_size,
        host_currency=currency,
        departure_date=datetime.datetime.now() + datetime.timedelta(days=30),
        return_date=None,
    )
    duration = get_direct_flight_duration(sample_request)
    assert duration is not None


def test_get_one_way_flights():
    sample_request = FlightRequest(
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        family_size=family_size,
        host_currency=currency,
        departure_date=datetime.datetime.now() + datetime.timedelta(days=30),
        return_date=None,
    )
    result, _ = get_flights_from_request(sample_request)
    save_flights_to_json(result, "one_way_flights.json")
    assert result is not None


def test_calculate_flight_cost_round_trip():
    sample_request = FlightRequest(
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        family_size=family_size,
        host_currency=currency,
        departure_date=datetime.datetime.now() + datetime.timedelta(days=30),
        return_date=datetime.datetime.now() + datetime.timedelta(days=60),
    )
    result, _ = get_flights_from_request(sample_request)
    save_flights_to_json(result, "round_trip_flights.json")
    assert result is not None
