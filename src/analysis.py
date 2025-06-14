import numpy as np

from src.flights import ParsedFlight


def get_average_cost(flights: list[ParsedFlight]) -> tuple[int, int]:
    prices, minutes = biased_prices(flights)
    rounded = round_with_margins(float(np.mean(prices)))
    return rounded, int(minutes)


def iqr_filter(prices: np.ndarray, multiplier=1.5) -> np.ndarray:
    q1 = np.percentile(prices, 25)
    q3 = np.percentile(prices, 75)
    iqr = q3 - q1

    filtered = [q1 - multiplier * iqr <= p <= q3 + multiplier * iqr for p in prices]
    return np.array(filtered)


def biased_prices(
    flights: list[ParsedFlight],
    best_multiplier: int = 2,
) -> tuple[np.ndarray, float]:
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
    mean_duration = np.mean(durations[mask])
    return prices, float(mean_duration)


def round_with_margins(price: float) -> int:
    price_with_margins = price * 1.1
    rounded = int(np.ceil(price_with_margins / 25) * 25)
    return rounded
