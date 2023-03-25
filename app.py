from flask import Flask, render_template
import requests

app = Flask(__name__)

# Binance API endpoints
BASE_URL = "https://api.binance.com/api/v3"
EXCHANGE_INFO_URL = BASE_URL + "/exchangeInfo"
TICKER_PRICE_URL = BASE_URL + "/ticker/price"

@app.route("/")
def home():
    # Get exchange info from Binance API
    exchange_info = requests.get(EXCHANGE_INFO_URL).json()

    # Get ticker prices from Binance API
    ticker_prices = requests.get(TICKER_PRICE_URL).json()

    # Filter out symbols that are not available for trading
    symbols_available_for_trading = [symbol for symbol in exchange_info["symbols"] if symbol["status"] == "TRADING"]

    # Calculate triangular arbitrage profit for each symbol
    triangular_arbitrage_profits = []
    for symbol in symbols_available_for_trading:
        # Extract base and quote currencies
        base_currency = symbol["baseAsset"]
        quote_currency = symbol["quoteAsset"]
        
        # Check if there are any pairs that can be used for triangular arbitrage
        for pair in exchange_info["symbols"]:
            if pair["baseAsset"] == quote_currency:
                for pair2 in exchange_info["symbols"]:
                    if pair2["baseAsset"] == pair["quoteAsset"] and pair2["quoteAsset"] == base_currency:
                        # Calculate triangular arbitrage profit assuming no trading fee and initial investment of 100 USDT
                        rate1 = float([price["price"] for price in ticker_prices if price["symbol"] == symbol["symbol"]][0])
                        rate2 = float([price["price"] for price in ticker_prices if price["symbol"] == pair["symbol"]][0])
                        rate3 = float([price["price"] for price in ticker_prices if price["symbol"] == pair2["symbol"]][0])
                        triangular_arbitrage_profit = 100 * rate1 / rate2 * rate3 / 100 - 100
                        if triangular_arbitrage_profit > 0:
                            triangular_arbitrage_profits.append((symbol["symbol"], triangular_arbitrage_profit))

    # Render template with data
    return render_template("index.html", symbols=symbols_available_for_trading, triangular_arbitrage_profits=triangular_arbitrage_profits)

if __name__ == "__main__":
    app.run(debug=True)
