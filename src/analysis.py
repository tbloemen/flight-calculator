from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pendulum

from src.flights import FlightRequest, ParsedFlight, load_currency_converter
from src.util import get_template_dir

converter = load_currency_converter()


@dataclass(frozen=True, order=True)
class ParetoFlight:
    price: float
    rounded_price: int
    duration: str
    converted: str


@dataclass
class Advice:
    """
    The price is in euros. The duration is in minutes.
    """

    pareto_flights: list[ParetoFlight]
    pareto_path: str
    name: str
    request: FlightRequest
    departure_date_str: str
    return_date_str: str | None
    buying_time: str
    avg_duration: float


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
    file: str,
    title: str,
) -> None:
    plt.figure(figsize=(10, 6))
    plt.scatter(minutes, prices, c="lightgray", label="All flights")
    plt.scatter(
        sorted_pareto_minutes, sorted_pareto_prices, c="red", label="Best flights"
    )
    plt.plot(sorted_pareto_minutes, sorted_pareto_prices, "r--", alpha=0.5)

    plt.xlabel("Duration (minutes)")
    plt.ylabel("Price (€)")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(get_template_dir() + "/" + file)


def get_advice(
    flights: list[ParsedFlight],
    filename: str,
    name: str,
    request: FlightRequest,
    buying_time: str,
    avg_duration: float,
) -> Advice:
    prices, minutes = biased_prices(flights)
    title = f"{request.departure_airport}-{request.arrival_airport}: Price vs Duration"

    N = len(prices)
    pareto_indices = [i for i in range(N) if not is_dominated(i, prices, minutes)]

    pareto_minutes = minutes[pareto_indices]
    pareto_prices = prices[pareto_indices]

    sorted_indices = np.argsort(pareto_minutes)
    sorted_pareto_minutes = pareto_minutes[sorted_indices]
    sorted_pareto_prices = pareto_prices[sorted_indices]

    plot_flights(
        minutes, prices, sorted_pareto_minutes, sorted_pareto_prices, filename, title
    )
    departure_date_str = request.departure_date.to_formatted_date_string()
    return_date_str = None
    if request.return_date:
        return_date_str = request.return_date.to_formatted_date_string()

    pareto_flights = set()
    for i in range(len(pareto_indices)):
        rounded = round_with_margins(pareto_prices[i])
        duration = pendulum.duration(minutes=int(pareto_minutes[i]))
        converted = converter.convert(
            rounded, "EUR", request.host_currency.abbreviation
        )
        converted_str = "{:.2f}".format(converted)
        pareto_flight = ParetoFlight(
            pareto_prices[i], rounded, duration.in_words(), converted_str
        )
        pareto_flights.add(pareto_flight)

    return Advice(
        pareto_flights=sorted(list(pareto_flights)),
        pareto_path=filename,
        name=name.title(),
        request=request,
        departure_date_str=departure_date_str,
        return_date_str=return_date_str,
        buying_time=buying_time,
        avg_duration=avg_duration,
    )


def iqr_filter(prices: np.ndarray, multiplier=1.5) -> np.ndarray:
    q1 = np.percentile(prices, 25)
    q3 = np.percentile(prices, 75)
    iqr = q3 - q1

    filtered = [q1 - multiplier * iqr <= p <= q3 + multiplier * iqr for p in prices]
    return np.array(filtered)


def biased_prices(
    flights: list[ParsedFlight],
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

    prices = np.repeat(old_prices, repeats)
    new_durations = np.repeat(durations, repeats)
    return prices, new_durations


def round_with_margins(price: float) -> int:
    price_with_margins = price * 1.1
    rounded = int(np.ceil(price_with_margins / 25) * 25)
    return rounded
