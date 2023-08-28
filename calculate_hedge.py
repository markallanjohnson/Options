import sys

from yahoo_fin import stock_info, options

def calculate_hedge(position, ticker="SPY", otm_percent=0.30):
    # Constants
    ANNUAL_BUDGET_PERCENT = 0.033  # 3.3%
    MONTHS = 12

    # Calculate monthly budget for put options
    annual_budget = position * ANNUAL_BUDGET_PERCENT
    monthly_budget = annual_budget / MONTHS

    # Get current price of the specified ticker
    current_price = stock_info.get_live_price(ticker)

    # Calculate out-of-the-money strike
    otm_strike = current_price * (1 - otm_percent)

    # Get available expiration dates for the ticker
    expiration_dates = options.get_expiration_dates(ticker)
    if not expiration_dates:
        print(f"No expiration dates found for {ticker}.")
        sys.exit(1)
    # Use the nearest expiration date
    expiration_date = expiration_dates[0]

    # Fetch put options for the ticker for the given expiration date
    puts = options.get_puts(ticker, expiration_date)

    # Find the put option closest to the calculated OTM strike
    puts['Strike Difference'] = abs(puts['Strike'] - otm_strike)
    target_put = puts.nsmallest(1, 'Strike Difference')

    if target_put.empty:
        return None

    put_price = target_put['Last Price'].values[0]
    implied_volatility = target_put['Implied Volatility'].values[0]
    contracts_to_buy = monthly_budget / (put_price * 100)  # 1 contract = 100 shares

    return {
        "Current Price": current_price,
        "Expiration Date": expiration_date,
        "OTM Strike": otm_strike,
        "Put Price": put_price,
        "Implied Volatility": implied_volatility,
        "Contracts to Buy": contracts_to_buy,
        "Total Cost": contracts_to_buy * put_price * 100
    }

if __name__ == "__main__":
    position = float(input("Enter your portfolio value: "))
    ticker = input("Enter the ticker (default is SPY): ") or "SPY"
    otm_percent = float(input("Enter the percentage out of the money (default is 0.30): ") or 0.30)

    result = calculate_hedge(position, ticker, otm_percent)

    if result:
        print("\nStrategy Details:")
        print("Underlying's Current Price:", result["Current Price"])
        print("Expiration Date:", result["Expiration Date"])
        print("OTM Strike Price:", result["OTM Strike"])
        print("Put Option Price:", result["Put Price"])
        print("Implied Volatility:", result["Implied Volatility"])
        print("Contracts to Buy:", int(result["Contracts to Buy"]))
        print("Total Cost:", result["Total Cost"])
    else:
        print(f"Couldn't find suitable option for {ticker}.")
