# import yfinance as yf

def get_stock_sectors(tickers):
    stock_sectors = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            sector = info.get('sector', 'Unknown')  # Get sector, default to 'Unknown' if not available
            stock_sectors[ticker] = sector
        except Exception as e:
            stock_sectors[ticker] = f"Error: {str(e)}"  # Handle errors for missing or invalid data
    
    return stock_sectors

# # Example usage
# tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
# sectors = get_stock_sectors(tickers)
# print(sectors)


# import yfinance as yf

def get_stock_regions(tickers):
    stock_regions = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            region = info.get('country', 'Unknown')  # Default to 'Unknown' if country is not available
            stock_regions[ticker] = region
        except Exception as e:
            stock_regions[ticker] = f"Error: {str(e)}"  # Handle errors for missing or invalid data
    return stock_regions

# # Example usage
# tickers = ['AAPL', 'TSLA', 'BABA', 'SONY', 'TSM']
# regions = get_stock_regions(tickers)
# print(regions)


# import yfinance as yf

# def get_live_price(ticker):
#     """
#     Fetch the live price of a stock using yfinance.

#     :param ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
#     :return: Current live price of the stock
#     """
#     try:
#         stock = yf.Ticker(ticker)
#         live_price = stock.fast_info['last_price']  # Fast info is faster and optimized for live data
#         return live_price
#     except Exception as e:
#         return f"Error fetching price for {ticker}: {str(e)}"

# # Example usage
# ticker = 'AAPL'
# live_price = get_live_price(ticker)
# print(f"Live price of {ticker}: ${live_price}")



# import yfinance as yf

# # List of tickers from the screenshot
# tickers = ["PRFX", "OMER", "PRTA", "SOC"]

# # Fetch stock data
# for ticker in tickers:
#     stock = yf.Ticker(ticker)
#     info = stock.info

#     print(f"Ticker: {ticker}")
#     print(f"Price: {info.get('regularMarketPrice', 'N/A')} USD")
#     print(f"Change %: {info.get('regularMarketChangePercent', 'N/A')}%")
#     print(f"Volume: {info.get('volume', 'N/A')} shares")
#     print(f"Market Cap: {info.get('marketCap', 'N/A')} USD")
#     print(f"Sector: {info.get('sector', 'N/A')}")
#     print("-------")



# import yfinance as yf

# ticker = "SOC"
# stock = yf.Ticker(ticker)
# info = stock.info

# # Print all keys and values in the info dictionary
# for key, value in info.items():
#     print(f"{key}: {value}")


import yfinance as yf

# Function to calculate a simple technical rating
def get_technical_rating(price, sma_50, sma_200):
    if price > sma_50 > sma_200:
        return "Strong Buy"
    elif price > sma_50:
        return "Buy"
    elif price < sma_50:
        return "Sell"
    else:
        return "Hold"

# List of tickers to analyze
tickers = ["PRFX", "OMER", "PRTA", "SOC"]

for ticker in tickers:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    # Get the latest price and calculate moving averages
    price = hist["Close"].iloc[-1]
    sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1]
    sma_200 = hist["Close"].rolling(window=200).mean().iloc[-1]

    # Extract other stock information
    info = stock.info
    prev_close = info.get("regularMarketPreviousClose")
    volume = info.get("volume")
    market_cap = info.get("marketCap")
    sector = info.get("sector")

    # Calculate price change and percentage change
    if prev_close:
        price_change = price - prev_close
        percent_change = (price_change / prev_close) * 100
    else:
        price_change = "N/A"
        percent_change = "N/A"

    # Calculate volume * price
    vol_price = volume * price if volume and price else "N/A"

    # Calculate technical rating
    technical_rating = get_technical_rating(price, sma_50, sma_200)

    # Display stock data
    print(f"Ticker: {ticker}")
    print(f"Price: {price:.2f} USD")
    print(f"Price Change: {price_change:.2f} USD" if price_change != "N/A" else "Price Change: N/A")
    print(f"Change %: {percent_change:.2f}%" if percent_change != "N/A" else "Change %: N/A")
    print(f"Volume: {volume} shares")
    print(f"Volume × Price: {vol_price:.2f}" if vol_price != "N/A" else "Volume × Price: N/A")
    print(f"Market Cap: {market_cap} USD")
    print(f"Sector: {sector}")
    print(f"50-Day SMA: {sma_50:.2f} USD")
    print(f"200-Day SMA: {sma_200:.2f} USD")
    print(f"Technical Rating: {technical_rating}")
    print("-------")

