import csv
import io
import pkgutil
import re
from dataclasses import dataclass
from typing import Literal

import currency_converter
import pendulum
from airportsdata import load
from babel.numbers import get_currency_name, get_currency_symbol
from fast_flights import (
    Airport,
    Flight,
    FlightData,
    Passengers,
    get_flights,
    search_airport,
)
from pendulum import Date, DateTime


def load_airports() -> dict[str, dict[str, str]]:
    # Load CSV from within the PyInstaller bundle (works with --onefile)
    data = pkgutil.get_data(__name__, "resources/airports.csv")
    if data is None:
        raise RuntimeError("Could not load airports.csv")
    airports = {}
    with io.StringIO(data.decode("utf-8")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["iata"].upper()
            if code:
                airports[code] = row
    return airports


fetch_mode: Literal["local"] = "local"
airports = load_airports()
converter = currency_converter.CurrencyConverter()


@dataclass
class Currency:
    name: str
    symbol: str
    abbreviation: str


@dataclass
class FlightRequest:
    departure_airport: str
    arrival_airport: str
    family_size: int
    host_currency: Currency
    departure_date: Date
    return_date: Date | None


@dataclass
class ParsedFlight:
    name: str
    departure: DateTime
    arrival: DateTime
    stops: int
    price: float


def parse_currency(abbreviation: str) -> Currency:
    abbreviation = abbreviation.upper()
    if not converter.currencies:
        raise Exception("Error during loading of the currencies")
    if abbreviation not in converter.currencies:
        raise ValueError(f"{abbreviation} is not a valid currency.")
    name = get_currency_name(abbreviation, locale="en_US")
    symbol = get_currency_symbol(abbreviation, locale="en_US")
    return Currency(name=name, symbol=symbol, abbreviation=abbreviation)


def get_airport_code(airport: str) -> Airport:
    codes = search_airport(airport.replace(" ", "_"))
    if len(codes) == 0:
        raise ValueError(f"Airport was not found with the string {airport}")
    return codes[0]


def get_hours(time_str):
    match = re.match(r"^(\d+)\s*hr$", time_str.strip())
    if match:
        return int(match.group(1))
    else:
        raise Exception(f"Invalid time format: {time_str}")


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


def parse_flight_time(time_str: str, timezone: str) -> DateTime:
    # Remove "on " and append year
    year = pendulum.now().year
    clean_str = time_str.replace("on ", "") + f" {year}"
    # Format: "10:30 AM Sun, Jul 13 2025"
    return pendulum.from_format(clean_str, "h:mm A ddd, MMM D YYYY", tz=timezone)


def get_timezone(airport: str) -> str:
    airport_code = airport.upper()
    info = airports.get(airport_code)
    if not info:
        raise ValueError(f"Unknown airport code: {airport_code}")
    return info["tz"]


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
    trip = "one-way"
    seat = "economy"
    passengers = Passengers(adults=request.family_size)

    flights = get_flights(
        flight_data=[flight_data],
        trip=trip,
        seat=seat,
        passengers=passengers,
        fetch_mode=fetch_mode,
    )
    first_parsed_flight = parse_flight(
        flights.flights[0], request.departure_airport, request.arrival_airport
    )
    delta = first_parsed_flight.arrival.diff(first_parsed_flight.departure)

    return delta.in_hours()


def get_raw_flights(
    request: FlightRequest, economy_hours: int = 5
) -> tuple[list[Flight], str]:
    duration = get_direct_flight_duration(request)

    seat = "economy" if duration <= economy_hours else "business"

    strf_time_string = "%Y-%m-%d"
    flight_data = FlightData(
        date=request.departure_date.strftime(strf_time_string),
        from_airport=request.departure_airport,
        to_airport=request.arrival_airport,
    )
    fd_array = [flight_data]
    trip = "one-way"
    if request.return_date:
        trip = "round-trip"
        return_trip = FlightData(
            date=request.return_date.strftime(strf_time_string),
            from_airport=request.arrival_airport,
            to_airport=request.departure_airport,
        )
        fd_array.append(return_trip)
    passengers = Passengers(adults=request.family_size)

    flights = get_flights(
        flight_data=fd_array,
        trip=trip,
        seat=seat,
        passengers=passengers,
        fetch_mode=fetch_mode,
    )
    return flights.flights, flights.current_price


def parse_flight(
    flight: Flight, departure_airport: str, arrival_airport: str
) -> ParsedFlight:
    departure_timezone = get_timezone(departure_airport)
    arrival_timezone = get_timezone(arrival_airport)
    departure_dt = parse_flight_time(flight.departure, departure_timezone)
    arrival_dt = parse_flight_time(flight.arrival, arrival_timezone)

    if flight.arrival_time_ahead.strip() == "+1":
        arrival_dt = arrival_dt.add(days=1)

    price = deformat_price(flight.price)

    parsed_flight = ParsedFlight(
        name=flight.name,
        departure=departure_dt,
        arrival=arrival_dt,
        stops=flight.stops,
        price=price,
    )
    return parsed_flight


def get_parsed_flights(request: FlightRequest) -> list[ParsedFlight]:
    flights, _ = get_raw_flights(request)

    parsed_flights = []
    for flight in flights:
        try:
            parsed_flight = parse_flight(
                flight, request.departure_airport, request.arrival_airport
            )
            parsed_flights.append(parsed_flight)
        except ValueError:
            print(f"Could not parse the flight {flight.name}. Skipping...")
    return parsed_flights
