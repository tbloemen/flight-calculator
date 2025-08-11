import os
import subprocess
import sys

from src.analysis import Advice, get_average_cost
from src.flights import (
    FlightRequest,
    get_parsed_flights,
)
from src.input import merge_sheets, parse_df
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
    # ensure playwright is installed correctly
    if getattr(sys, 'frozen', False):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(
            os.path.dirname(__file__), "playwright_browsers"
        )
    sheets = merge_sheets()
    requests = parse_df(sheets)
    print("Analyzing requests...")
    advices = analyze_request(requests)
    print("Creating PDF report...")
    create_pdf(advices)


if __name__ == "__main__":
    main()
