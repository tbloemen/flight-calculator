import pendulum
import pandas

from src.analysis import get_average_cost
from src.flights import (
    FlightRequest,
    get_airport_code,
    get_parsed_flights,
    parse_currency,
)


def print_result(price: int, minutes: int):
    print(
        f"The average sufficient price is {price} euros. The average duration is {int(minutes/60)} hours and {minutes % 60 } minutes."
    )


def analyze_request(request: FlightRequest) -> None:
    flights_now = get_parsed_flights(request)
    price_now, duration_now = get_average_cost(flights_now)
    print_result(price_now, duration_now)


def take_cli_input() -> FlightRequest:
    departure_airport_str = input("At what city or airport will you depart?\n")
    departure_airport = get_airport_code(departure_airport_str)
    departure_date_str = input(
        f"At what date will you depart?\nPlease input as YYYY-MM-DD. Example: {pendulum.today().to_date_string()}\n"
    )
    departure_date = pendulum.parse(departure_date_str, strict=False)

    arrival_airport_str = input("At what city or airport will you arrive?\n")
    arrival_airport = get_airport_code(arrival_airport_str)

    is_round_trip_str = input(
        "Will it be a round trip or a one-way trip?\nPlease enter 'y' if it is a round trip, or 'n' if it is a one-way trip.\n"
    )
    is_round_trip = is_round_trip_str.lower() == "y"

    if is_round_trip:
        return_date_str = input(
            f"At what date will you return?\nPlease input as YYYY-MM-DD. Example: {pendulum.today()}\n"
        )
        return_date = pendulum.parse(return_date_str, strict=False)
    else:
        return_date = None

    family_size = int(
        input("With how many people will you travel (including yourself)?\n")
    )
    currency_str = input("What is your home currency?\n")
    host_currency = parse_currency(currency_str)
    request = FlightRequest(
        departure_airport,
        arrival_airport,
        family_size,
        host_currency,
        departure_date,  # type: ignore
        return_date,  # type: ignore
    )
    return request


def take_sheet_input(filename: str) -> list[tuple[str, FlightRequest | None]]:
    df = pandas.read_excel(filename)
    print(df)
    request_list = []
    for entry in df.values.tolist():
        try:
            print(entry)
            name: str = entry[0]
            departure_airport = get_airport_code(entry[1])
            departure_date = pendulum.parse(entry[2], strict=False)
            arrival_airport = get_airport_code(entry[3])
            return_date = None
            if entry[4] != "":
                return_date = pendulum.parse(entry[4])
            family_size = int(entry[5])
            host_currency = parse_currency(entry[6])
            FlightRequest(
                departure_airport=departure_airport,
                arrival_airport=arrival_airport,
                family_size=family_size,
                host_currency=host_currency,
                departure_date=departure_date,  # type: ignore
                return_date=return_date,  # type: ignore
            )
            request_list.append((name.capitalize(), FlightRequest))
        except ValueError:
            request_list.append(("Error", []))
    return request_list


def main():
    print("Hello from flight-calculator!")
    # request = take_cli_input()
    # analyze_request(request)
    requests = take_sheet_input("input.ods")
    print(requests)


if __name__ == "__main__":
    main()
