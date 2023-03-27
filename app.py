from flask import Flask, render_template
import requests
import json

app = Flask(__name__)

def get_exchange_data():
    exchanges = {
        "binance": "https://api.binance.com/api/v3/ticker/price",
        "bitfinex": "https://api.bitfinex.com/v1/pubticker/BTCUSD",
        "bittrex": "https://api.bittrex.com/api/v1.1/public/getticker?market=USD-BTC",
        "coinbase": "https://api.coinbase.com/v2/prices/BTC-USD/spot",
        "kraken": "https://api.kraken.com/0/public/Ticker?pair=XBTUSD"
    }

    exchange_data = {}
    for exchange, url in exchanges.items():
        response = requests.get(url)
        data = json.loads(response.text)

        # extract data for all coins
        if exchange == "binance":
            for coin in data:
                if coin["symbol"].endswith("USDT"):
                    symbol = coin["symbol"][:-4]
                    price = float(coin["price"])
                    if symbol in exchange_data:
                        exchange_data[symbol][exchange] = price
                    else:
                        exchange_data[symbol] = {exchange: price}
        elif exchange == "bitfinex":
            symbol = "BTC"
            price = float(data["last_price"])
            if symbol in exchange_data:
                exchange_data[symbol][exchange] = price
            else:
                exchange_data[symbol] = {exchange: price}
        elif exchange == "bittrex":
            symbol = "BTC"
            price = float(data["result"]["Last"])
            if symbol in exchange_data:
                exchange_data[symbol][exchange] = price
            else:
                exchange_data[symbol] = {exchange: price}
        elif exchange == "coinbase":
            symbol = "BTC"
            price = float(data["data"]["amount"])
            if symbol in exchange_data:
                exchange_data[symbol][exchange] = price
            else:
                exchange_data[symbol] = {exchange: price}
        elif exchange == "kraken":
            symbol = "BTC"
            price = float(data["result"]["XXBTZUSD"]["c"][0])
            if symbol in exchange_data:
                exchange_data[symbol][exchange] = price
            else:
                exchange_data[symbol] = {exchange: price}

    return exchange_data

def get_arbitrage_opportunities(exchange_data):
    opportunities = []
    for coin, prices in exchange_data.items():
        max_price = max(prices.values())
        min_price = min(prices.values())
        if max_price > min_price:
            arb = ((max_price - min_price) / min_price) * 100
            opportunities.append({"coin": coin, "arb": arb})
    return sorted(opportunities, key=lambda x: x["arb"], reverse=True)

@app.route("/")
def home():
    exchange_data = get_exchange_data()
    opportunities = get_arbitrage_opportunities(exchange_data)
    return render_template("home.html", exchange_data=exchange_data, opportunities=opportunities)

if __name__ == "__main__":
    app.run(debug=True)
