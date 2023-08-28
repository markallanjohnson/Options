import sys
from yahoo_fin import options

def get_option_prices(ticker, expiration_date=None):
    """Retrieve option prices for a given ticker and expiration date."""
    try:
        # Get available expiration dates for the ticker
        dates = options.get_expiration_dates(ticker)

        # If no expiration_date provided, or the provided date isn't available
        # use the nearest expiration date
        if expiration_date not in dates:
            print(f"Using the nearest expiration date: {dates[0]}")
            expiration_date = dates[0]

        # Fetch call and put data for the given ticker and expiration date
        calls = options.get_calls(ticker, expiration_date)
        puts = options.get_puts(ticker, expiration_date)

        return calls, puts

    except Exception as e:
        print(f"Error: {e}")
        return None, None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py TICKER [EXPIRATION_DATE]")
        sys.exit(1)

    ticker = sys.argv[1]
    expiration_date = sys.argv[2] if len(sys.argv) > 2 else None
    calls, puts = get_option_prices(ticker, expiration_date)

    if calls is not None and puts is not None:
        print("\nCALLS:\n", calls)
        print("\nPUTS:\n", puts)
