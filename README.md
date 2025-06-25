# Home Leave Allowance Tool

Home Leave Allowance Tool, or HLA-tool for short, generates a report on the flights that are available according to specifications provided in an input excel document. This script uses live data from [Google Flights](https://www.google.com/travel/flights) and the [European Central Bank](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html) for currency conversion.

## Installation

HLA-Tool uses [wkhtmltopdf](https://wkhtmltopdf.org/index.html) for generating the pdfs. On Windows, that means you need to [download the installer](https://wkhtmltopdf.org/downloads.html) and run it. 

Next, windows needs to know that this program exists, and there this program must be added to your path. This can be done by pressing `win` + `s` (opening the search bar), and entering "environment variables". That will look like this: ![Image of environment variables](images/search.png) 

We will add the 

### From source

Clone the repository. This project uses [uv](https://github.com/astral-sh/uv) to manage python dependencies, so to run the application, enter the following in the terminal (assuming uv is installed):

```bash
uv run main.py
```

### From executable

You could also directly copy the executable as generated in the most recent release. This file is called `HLA-tool.exe`.

## Usage

HLA-tool will take any excel-like document that follows the data convention given in the example `input.xlsx`, and analyze the flights, and turn it into a report. It is expected to take ~10 seconds for 3 entries. Some important notes on the data you need to provide:

- The departure and arrival airports take in an airport code, following the [IATA](https://www.iata.org/en/publications/directories/code-search/) standard. For example: LDH, AMS, BER...
- The date fields follow the YYYY-MM-DD convention.
- If it is a one-way trip, you should leave the return date empty.
- The currency should be inputted as the 3-letter abbreviation used by the European Bank. For example: USD, EUR, JPY...

Continuously asking flights from the website is an expensive operation, and might lead to your ip-address being blacklisted. Please don't run HLA-tool repeatedly for large amounts of requests. Use at your own risk.
