# Home Leave Allowance Tool

The Home Leave Allowance Tool (HLA-tool) creates a simple, printable report of flight options based on details you provide in an Excel file. It looks up live flight information from Google Flights and uses exchange rates from the European Central Bank to convert prices to your chosen currency.

## Quick start (recommended for most users)

- Download the latest release and run the app:
  - Windows: use `HLA-tool.exe` from the “Releases” page.
- Prepare your input file:
  - Use the included `input.xlsx` as a template.
  - The input file you use can have any name, but it must have the same structure as `input.xlsx`.
  - Save it in the same folder as the app.
- Run the app and wait for the report:
  - The tool typically needs about 10 seconds for 3 entries (this varies).
  - Your report will be saved as `report_<current date>.pdf` in the same folder.

Important:

- You need an active internet connection.
- Flight lookups are intensive and repeated large runs may cause temporary blocking by the data provider. Please run responsibly.

## How to fill in the input file

Each row represents one trip you want to check. The columns should follow these rules:

- From / To airport: use IATA airport codes (e.g., AMS, BER, LHR). You can look up codes on the IATA website.
- Dates: use the format YYYY-MM-DD (for example, 2025-01-09).
- One-way trips: leave the return date empty.
- Currency: use a 3-letter code recognized by the European Central Bank (e.g., EUR, USD, JPY).

Tips:

- Keep your entries concise. Running very large lists can be slow and may trigger rate limiting.
- If the tool reports that it cannot find a flight, check the airport codes and dates.

## Output

- The tool produces a PDF report named `report_<current date>.pdf`.
- The report summarizes suitable flight options and shows prices converted to your selected currency.

## Data sources and limitations

- Flight data: Google Flights (live lookups; availability and prices can change quickly).
- Exchange rates: European Central Bank daily reference rates.
- Limitations:
  - Frequent or large-volume runs may cause temporary blocking by the flight data source.
  - Results depend on current availability; if a flight disappears, it may not appear in the report.

## Troubleshooting

- No results found:
  - Double-check IATA codes and dates.
  - Try alternate dates or nearby airports.
- The app seems slow:
  - Large input files can take several minutes.
  - Run fewer rows at a time.
- Currency issues:
  - Confirm you’re using valid 3-letter ECB currency codes (e.g., EUR, USD).
- Still stuck?
  - Try a small test (one row) with a major route (e.g., AMS–LHR) and today + 30 days.

## Installation (advanced)

If you prefer to run from source:

1. Install Typst (required to generate the PDF report)
   - See https://typst.app/docs/install/

2. Install UV (used to manage Python dependencies)
   - See https://github.com/astral-sh/uv

3. Run the tool from the project folder:
   ```bash
   uv run HLA-tool.py
   ```

## Safety and privacy

- The tool reads only your local excel-like files and writes `report_<current date>.pdf` to the same folder.
- It accesses external websites to retrieve flight and exchange rate data.
- Use at your own risk; availability of data sources may change.

## FAQ

- Do I need internet?
  - Yes, for live flight data and exchange rates.
- Which operating systems are supported?
  - A Windows executable is provided. Advanced users on other systems can run from source.
- Where do airport and currency codes come from?
  - Airport codes follow IATA standards; currency codes follow ECB references.
