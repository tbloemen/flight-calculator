from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pendulum

from src.flights import ParsedFlight


@dataclass
class ParetoFlight:
    price: float
    rounded_price: int
    duration: pendulum.Duration


@dataclass
class Advice:
    """
    The price is in euros. The duration is in minutes.
    """

    pareto_flights: list[ParetoFlight]
    pareto_path: Path


def is_dominated(i: int, prices: np.ndarray, durations: np.ndarray) -> bool:
    for j in range(len(durations)):
        if (prices[j] <= prices[i] and durations[j] <= durations[i]) and (
            prices[j] < prices[i] or durations[j] < durations[i]
        ):
            return True
    return False


def plot_flights(
    minutes: np.ndarray,
    prices: np.ndarray,
    sorted_pareto_minutes: np.ndarray,
    sorted_pareto_prices: np.ndarray,
    file: Path,
) -> None:
    plt.figure(figsize=(10, 6))
    plt.scatter(minutes, prices, c="lightgray", label="All flights")
    plt.scatter(
        sorted_pareto_minutes, sorted_pareto_prices, c="red", label="Best flights"
    )
    plt.plot(sorted_pareto_minutes, sorted_pareto_prices, "r--", alpha=0.5)

    plt.xlabel("Duration (minutes)")
    plt.ylabel("Price (€)")
    plt.title("Flight Pareto Front: Price vs Duration")
    plt.legend()
    plt.grid(True)
    plt.savefig(file)


def get_average_cost(flights: list[ParsedFlight], filename: str) -> Advice:
    prices, minutes = biased_prices(flights)

    file = Path.cwd() / filename
    N = len(prices)
    pareto_indices = [i for i in range(N) if not is_dominated(i, prices, minutes)]

    pareto_minutes = minutes[pareto_indices]
    pareto_prices = prices[pareto_indices]

    sorted_indices = np.argsort(pareto_minutes)
    sorted_pareto_minutes = pareto_minutes[sorted_indices]
    sorted_pareto_prices = pareto_prices[sorted_indices]

    plot_flights(minutes, prices, sorted_pareto_minutes, sorted_pareto_prices, file)

    pareto_flights = []
    for i in range(len(pareto_indices)):
        rounded = round_with_margins(pareto_prices[i])
        duration = pendulum.duration(minutes=int(pareto_minutes[i]))
        pareto_flight = ParetoFlight(pareto_prices[i], rounded, duration)
        pareto_flights.append(pareto_flight)

    return Advice(pareto_flights, file)


def iqr_filter(prices: np.ndarray, multiplier=1.5) -> np.ndarray:
    q1 = np.percentile(prices, 25)
    q3 = np.percentile(prices, 75)
    iqr = q3 - q1

    filtered = [q1 - multiplier * iqr <= p <= q3 + multiplier * iqr for p in prices]
    return np.array(filtered)


def biased_prices(
    flights: list[ParsedFlight],
    best_multiplier: int = 2,
) -> tuple[np.ndarray, np.ndarray]:
    repeats = np.zeros(len(flights), dtype=int)
    # remove flights with outlying durations
    durations = np.array(
        list(
            map(
                lambda flight: flight.arrival.diff(flight.departure).in_minutes(),
                flights,
            )
        )
    )
    old_prices = np.array(list(map(lambda flight: flight.price, flights)))

    has_normal_duration_mask = iqr_filter(durations)
    has_normal_price_mask = iqr_filter(old_prices)
    mask = has_normal_duration_mask * has_normal_price_mask

    repeats[mask] = 1
    # repeat best flights more times to bias the flights
    best_flights = np.array(list(map(lambda flight: flight.is_best, flights)))
    repeats[best_flights] *= best_multiplier

    prices = np.repeat(old_prices, repeats)
    new_durations = np.repeat(durations, repeats)
    return prices, new_durations


def round_with_margins(price: float) -> int:
    price_with_margins = price * 1.1
    rounded = int(np.ceil(price_with_margins / 25) * 25)
    return rounded
