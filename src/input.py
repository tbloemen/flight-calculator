import pandas
import pendulum

from src.flights import FlightRequest, parse_currency


def take_cli_input() -> FlightRequest:
    departure_airport = input("At what city or airport will you depart?\n")
    departure_date_str = input(
        f"At what date will you depart?\nPlease input as YYYY-MM-DD. Example: {pendulum.today().to_date_string()}\n"
    )
    departure_date = pendulum.parse(departure_date_str, strict=False)

    arrival_airport = input("At what city or airport will you arrive?\n")

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
    request_list = []
    for entry in df.values.tolist():
        try:
            name: str = entry[0]
            departure_airport = entry[1]
            departure_date = pendulum.instance(entry[2].to_pydatetime())
            arrival_airport = entry[3]
            return_date = None
            if not pandas.isnull(entry[4]):
                return_date = pendulum.instance(entry[4].to_pydatetime())
            family_size = int(entry[5])
            host_currency = parse_currency(entry[6])
            request = FlightRequest(
                departure_airport=departure_airport,
                arrival_airport=arrival_airport,
                family_size=family_size,
                host_currency=host_currency,
                departure_date=departure_date,  # type: ignore
                return_date=return_date,  # type: ignore
            )
            request_list.append((name.capitalize(), request))
        except ValueError as e:
            print(e)
            request_list.append(("Error", []))
    return request_list
