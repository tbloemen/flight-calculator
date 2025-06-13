import numpy as np

from src.flights import ParsedFlight


def get_average_cost(flights: list[ParsedFlight]):
    best_flights = filter(lambda flight: flight.is_best, flights)
    prices = np.array(list(map(lambda flight: flight.price, best_flights)))
    print(prices)
    return np.mean(prices)
