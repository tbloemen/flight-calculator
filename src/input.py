import re
from datetime import date
from pathlib import Path
from typing import Optional

import pandas
import pendulum
from pydantic import BaseModel, field_validator

from src.flights import FlightRequest, parse_currency


class RawFlightRequest(BaseModel):
    Name: str
    Departure_Airport_Code: str
    Departure_Date: date
    Arrival_Airport_Code: str
    Return_Date: Optional[date]
    Amount_Of_Passengers: int
    Home_Currency: str

    @field_validator("Departure_Airport_Code", "Arrival_Airport_Code")
    def valid_airport_code(cls, v: str) -> str:
        if not re.fullmatch(r"[A-Z]{3}", v):
            raise ValueError(f"Invalid airport code: {v}")
        return v

    @field_validator("Amount_Of_Passengers")
    def positive_passenger_count(cls, v) -> int:
        if isinstance(v, float):
            if not v.is_integer():
                raise ValueError("Passenger amount must be a whole number.")
            v = int(v)
        if v <= 0:
            raise ValueError("Passenger amound must be positive.")
        return int(v)

    @field_validator("Home_Currency")
    def valid_currency(cls, v: str) -> str:
        try:
            parse_currency(v)
        except KeyError:
            raise ValueError(f"Unknown currency: {v}")
        return v

    @field_validator("Return_Date", mode="before")
    def handle_nat(cls, v) -> date | None:
        if v is pandas.NaT or pandas.isna(v):
            return None
        return v


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


def merge_sheets() -> pandas.DataFrame:
    readers = {
        ".csv": pandas.read_csv,
        ".xlsx": pandas.read_excel,
        ".xls": pandas.read_excel,
        ".ods": lambda f: pandas.read_excel(f, engine="odf"),
    }
    all_dfs = []

    for ext, reader in readers.items():
        for filepath in Path.cwd().glob(f"*{ext}"):
            try:
                df = reader(filepath)
                all_dfs.append(df)
                print(f"Loaded {filepath} with {len(df)} rows.")
            except Exception as e:
                print(f"Could not read {filepath}:", e)

    if all_dfs:
        merged_df = pandas.concat(all_dfs, ignore_index=True)
        return merged_df
    else:
        raise ValueError("No readable Excel-like files found in the current directory.")


def parse_df(df: pandas.DataFrame) -> list[tuple[str, FlightRequest | None]]:
    request_list = []
    for _, entry in df.iterrows():
        try:
            raw = RawFlightRequest.model_validate(entry.to_dict())
            name = raw.Name.strip().title()
            request = FlightRequest(
                departure_airport=raw.Departure_Airport_Code,
                arrival_airport=raw.Arrival_Airport_Code,
                family_size=raw.Amount_Of_Passengers,
                host_currency=parse_currency(raw.Home_Currency),
                departure_date=pendulum.date(
                    raw.Departure_Date.year,
                    raw.Departure_Date.month,
                    raw.Departure_Date.day,
                ),
                return_date=(
                    pendulum.date(
                        raw.Return_Date.year, raw.Return_Date.month, raw.Return_Date.day
                    )
                    if raw.Return_Date
                    else None
                ),
            )
            request_list.append((name, request))
        except ValueError as e:
            print("Row validation failed:", e)
            request_list.append(("Error", None))
    return request_list
