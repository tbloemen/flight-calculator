from src.analysis import get_average_cost
from src.flights import (
    FlightRequest,
    get_parsed_flights,
)
from src.input import take_sheet_input


def print_result(price: int, minutes: int):
    print(
        f"The average sufficient price is {price} euros. The average duration is {int(minutes/60)} hours and {minutes % 60 } minutes."
    )


def analyze_request(requests: list[tuple[str, FlightRequest | None]]) -> None:
    for i, (name, request) in enumerate(requests):
        if request is None:
            continue
        filename = f"{i}_{name}.png"
        flights_now = get_parsed_flights(request)
        advice = get_average_cost(flights_now, filename)
        print(advice)


def main():
    print("Hello from flight-calculator!")
    # request = take_cli_input()
    # analyze_request(request)
    requests = take_sheet_input("input.ods")
    print(requests)
    analyze_request(requests)


if __name__ == "__main__":
    main()
