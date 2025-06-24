from src.analysis import Advice, get_average_cost
from src.flights import (
    FlightRequest,
    get_parsed_flights,
)
from src.input import take_sheet_input
from src.output import create_pdf


def analyze_request(requests: list[tuple[str, FlightRequest | None]]) -> list[Advice]:
    advices = []
    for i, (name, request) in enumerate(requests):
        if request is None:
            continue
        filename = f"{i}_{name.replace(' ', '_')}.png"
        flights_now = get_parsed_flights(request)
        advice = get_average_cost(flights_now, filename, name, request)
        advices.append(advice)
    return advices


def main():
    print("Hello from flight-calculator!")
    # request = take_cli_input()
    # analyze_request(request)
    requests = take_sheet_input("input.ods")
    print(requests)
    advices = analyze_request(requests)
    create_pdf(advices)


if __name__ == "__main__":
    main()
