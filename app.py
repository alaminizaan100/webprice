from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Define function to get coin information from API
def get_coin_info():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    coin_list = response.json()
    return coin_list

# Define function to check for triangular arbitrage opportunities
def check_triangular_arbitrage():
    url = "https://api.coingecko.com/api/v3/exchanges"
    response = requests.get(url)
    exchange_list = response.json()
    for exchange in exchange_list:
        if isinstance(exchange, dict) and "flags" in exchange and "triangular_arbitrage" in exchange["flags"]:
            return exchange["name"]
    return None


# Define route to display all coin information and check for triangular arbitrage opportunities
@app.route("/")
def display_coin_info():
    coin_list = get_coin_info()
    arbitrage_exchange = check_triangular_arbitrage()
    response = []
    for coin in coin_list:
        coin_info = {
            "id": coin["id"],
            "symbol": coin["symbol"],
            "name": coin["name"]
        }
        if arbitrage_exchange is not None:
            arbitrage_profit = get_triangular_arbitrage_profit(coin["id"], arbitrage_exchange)
            if arbitrage_profit is not None:
                coin_info["arbitrage_profit"] = arbitrage_profit
        response.append(coin_info)
    return jsonify(response)

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
