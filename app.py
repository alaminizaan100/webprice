from flask import Flask, render_template
import requests

app = Flask(__name__)

EXCHANGES = [
    {
        "name": "binance",
        "flags": ["triangular_arbitrage"]
    },
    {
        "name": "kucoin",
        "flags": ["triangular_arbitrage"]
    }
]

# Define function to get coin information from API
def get_coin_info():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    coin_list = response.json()
    return coin_list

# Define function to check for triangular arbitrage opportunities
def check_triangular_arbitrage(exchange_list):
    arbitrage_exchange = []
    for exchange in exchange_list:
        if "triangular_arbitrage" in exchange.get("flags", []):
            arbitrage_exchange.append(exchange["name"])
    return arbitrage_exchange

# Define route to display all coin information and check for triangular arbitrage opportunities
@app.route("/")
def display_coin_info():
    coin_list = get_coin_info()
    arbitrage_exchange = check_triangular_arbitrage(EXCHANGES)
    coin_info_list = []
    for coin in coin_list:
        coin_info = {
            "id": coin["id"],
            "symbol": coin["symbol"],
            "name": coin["name"]
        }
        for exchange in arbitrage_exchange:
            arbitrage_profit = get_triangular_arbitrage_profit(coin["id"], exchange)
            if arbitrage_profit is not None:
                coin_info[f"{exchange}_arbitrage_profit"] = arbitrage_profit
        coin_info_list.append(coin_info)
    return render_template("index.html", coin_info_list=coin_info_list)

# Define function to get triangular arbitrage profit for a given coin and exchange
def get_triangular_arbitrage_profit(coin_id, exchange_name):
    url = f"https://api.coingecko.com/api/v3/exchanges/{exchange_name}/triangular_arbitrage?currency_pairs={coin_id}"
    response = requests.get(url)
    data = response.json()
    if "error" not in data:
        profit = float(data[0]["rate"]) - 1
        return profit
    return None

if __name__ == '__main__':
    app.run(debug=True)
