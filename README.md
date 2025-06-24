# flight-calculator

Generates a report on the flights that are available according to specifications provided in an input excel document. This script uses live data from [Google Flights](https://www.google.com/travel/flights) and the [European Central Bank](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html) for currency conversion.

## Usage

Clone the repository. There are two packages needed to generate the pdfs:

1. [pandoc](https://pandoc.org/)
2. [Tectonic](https://tectonic-typesetting.github.io/en-US/index.html)

These both need to be installed to use the program. Additionally, this project uses [uv](https://github.com/astral-sh/uv) to manage python dependencies, so to run the application, enter the following in the terminal (assuming uv is installed):

```bash
uv run main.py
```

This will take any excel-like document that follows the data convention given in the example, and analyze the flights, and turn it into a report. Some important notes on the data you need to provide:

- The departure and arrival airports take in an airport code, following the [IATA](https://www.iata.org/en/publications/directories/code-search/) standard. For example: LDH, AMS, BER...
- The date fields follow the YYYY-MM-DD convention.
- If it is a one-way trip, you should leave the return date empty.
- The currency should be inputted as the 3-letter abbreviation used by the European Bank. For example: USD, EUR, JPY...

If you want to supply arguments yourself through the command line, run:

```bash
uv run main.py --cli
```
