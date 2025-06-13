from dataclasses import dataclass
from datetime import date
import re
from babel.numbers import get_currency_name, get_currency_symbol

from fast_flights import (
    Airport,
    Flight,
    FlightData,
    Passengers,
    get_flights,
    search_airport,
)

fetch_mode = "local"


@dataclass
class Currency:
    name: str
    symbol: str


@dataclass
class FlightRequest:
    departure_airport: Airport
    arrival_airport: Airport
    family_size: int
    host_currency: Currency
    departure_date: date
    return_date: date | None


def parse_currency(abbreviation: str) -> Currency:
    abbreviation = abbreviation.upper()
    name = get_currency_name(abbreviation)
    symbol = get_currency_symbol(abbreviation)
    return Currency(name=name, symbol=symbol)


def deformat_price(price: str) -> float:
    """
    Convert a formatted price string to a float.
    Handles various formats including currency symbols and commas.
    """
    # Remove currency symbol and commas
    price = price.replace("$", "").replace("€", "").replace(",", "")
    try:
        return float(price)
    except ValueError:
        raise ValueError(f"Invalid price format: {price}")


def get_airport_code(airport: str) -> Airport:
    return search_airport(airport.replace(" ", "_"))[0]


def get_hours(time_str):
    match = re.match(r"^(\d+)\s*hr$", time_str.strip())
    if match:
        return int(match.group(1))
    else:
        raise Exception(f"Invalid time format: {time_str}")


def get_direct_flight_duration(request: FlightRequest) -> int:
    """
    Gets the duration of the flight in hours.
    """
    flight_data = FlightData(
        date=request.departure_date.strftime("%Y-%m-%d"),
        from_airport=request.departure_airport,
        to_airport=request.arrival_airport,
        max_stops=0,
    )
    trip = "one-way" if request.return_date is None else "round-trip"
    seat = "economy"
    passengers = Passengers(adults=request.family_size)

    flights = get_flights(
        flight_data=[flight_data],
        trip=trip,
        seat=seat,
        passengers=passengers,
        fetch_mode=fetch_mode,
    )
    duration_str = flights.flights[0].duration

    return get_hours(duration_str)


def get_flights_from_request(request: FlightRequest) -> tuple[list[Flight], str]:
    flight_data = FlightData(
        date=request.departure_date.strftime("%Y-%m-%d"),
        from_airport=request.departure_airport,
        to_airport=request.arrival_airport,
        max_stops=2,
    )
    trip = "one-way" if request.return_date is None else "round-trip"
    duration = get_direct_flight_duration(request)
    seat = "economy" if duration < 5 else "business"
    passengers = Passengers(adults=request.family_size)

    flights = get_flights(
        flight_data=[flight_data],
        trip=trip,
        seat=seat,
        passengers=passengers,
        fetch_mode=fetch_mode,
    )
    return flights.flights, flights.current_price
