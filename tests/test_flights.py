import json
from dataclasses import asdict
from pathlib import Path

import pendulum

from src.flights import (
    FlightRequest,
    ParsedFlight,
    get_airport_code,
    get_direct_flight_duration,
    get_parsed_flights,
    parse_currency,
)

departure_airport = get_airport_code("amsterdam")
arrival_airport = get_airport_code("los angeles")
currency = parse_currency("USD")
family_size = 4


def save_flights_to_json(flights: list[ParsedFlight], filename: str):
    data_dir = Path.cwd() / "tests" / "data"
    data_dir.mkdir(exist_ok=True)
    file_path = data_dir / filename

    if not file_path.exists():

        def serialize(flight):
            d = asdict(flight)
            for foo in ["departure", "arrival"]:
                d[foo] = d[foo].to_iso8601_string()
            return d

        with file_path.open("w") as f:
            json.dump([serialize(flight) for flight in flights], f, indent=2)
        print(f"Saved {len(flights)} flights to {file_path}")
    else:
        print(f"File {file_path} already exists, not overwriting.")


def test_get_direct_flight_duration():
    sample_request = FlightRequest(
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        family_size=family_size,
        host_currency=currency,
        departure_date=pendulum.now() + pendulum.duration(days=30),
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
        departure_date=pendulum.now() + pendulum.duration(days=30),
        return_date=None,
    )
    result = get_parsed_flights(sample_request)
    save_flights_to_json(result, "one_way_flights.json")
    assert result is not None


def test_calculate_flight_cost_round_trip():
    sample_request = FlightRequest(
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        family_size=family_size,
        host_currency=currency,
        departure_date=pendulum.now() + pendulum.duration(days=30),
        return_date=pendulum.now() + pendulum.duration(days=60),
    )
    result = get_parsed_flights(sample_request)
    save_flights_to_json(result, "round_trip_flights.json")
    assert result is not None
