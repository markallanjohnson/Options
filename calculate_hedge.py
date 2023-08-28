import sys
import datetime

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
    
    
    # Filter expiration dates within the next two months
    today = datetime.date.today()
    two_months_later = today + datetime.timedelta(days=60)
    valid_expiration_dates = [date for date in expiration_dates if today <= datetime.datetime.strptime(date, '%B %d, %Y').date() <= two_months_later]

    # Placeholder for the best put option
    best_put_option = None
    for expiration_date in valid_expiration_dates:
        # Fetch put options for the ticker for the given expiration date
        puts = options.get_puts(ticker, expiration_date)
        puts['Strike Difference'] = abs(puts['Strike'] - otm_strike)
        target_put = puts.nsmallest(1, 'Strike Difference')
        
        if target_put.empty:
            continue
        
        put_price = target_put['Last Price'].values[0]
        implied_volatility = target_put['Implied Volatility'].values[0]
        
        if put_price <= 2:
            if not best_put_option or datetime.datetime.strptime(best_put_option["Expiration Date"], '%B %d, %Y').date() < datetime.datetime.strptime(expiration_date, '%B %d, %Y').date():
                best_put_option = {
                    "Current Price": current_price,
                    "Expiration Date": expiration_date,
                    "OTM Strike": otm_strike,
                    "Put Price": put_price,
                    "Implied Volatility": implied_volatility,
                    "Contracts to Buy": monthly_budget / (put_price * 100),  # 1 contract = 100 shares
                    "Total Cost": monthly_budget
                }

    return best_put_option

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
