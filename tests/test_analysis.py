import json
from pathlib import Path

import numpy as np
import pendulum

from src.analysis import (
    biased_prices,
    get_advice,
    iqr_filter,
    round_with_margins,
)
from src.flights import ParsedFlight


def load_flights_from_json(filename: str) -> list[ParsedFlight]:
    file_path = Path.cwd() / "tests" / "data" / filename
    with file_path.open("r") as f:
        data = json.load(f)
    return [
        ParsedFlight(
            is_best=entry["is_best"],
            name=entry["name"],
            departure=pendulum.parse(entry["departure"]),  # type: ignore
            arrival=pendulum.parse(entry["arrival"]),  # type: ignore
            stops=entry["stops"],
            price=entry["price"],
        )
        for entry in data
    ]


flights = load_flights_from_json("one_way_flights.json")


def test_get_average_price():
    price, minutes = get_advice(flights)
    print(f"Price: {price}")
    print(f"Duration: {int(minutes/60)} hours and {minutes % 60} minutes")
    assert price >= 0
    assert minutes >= 0


def test_get_rounded_price():
    assert round_with_margins(12) == 25
    assert round_with_margins(0) == 0
    assert round_with_margins(25) == 50
    assert round_with_margins(48) == 75
    assert round_with_margins(151) == 175


def test_biased_prices():
    prices = biased_prices(flights)
    assert len(prices) > 0


def test_iqr():
    prices, _ = biased_prices(flights)
    iqr_mask = iqr_filter(prices)
    avg = np.mean(prices[iqr_mask])
    print(f"IQR average: {avg}")
    print(f"Mean: {get_advice(flights)}")
    print(f"Biased mean: {np.mean(prices)}")
    assert avg >= 0
