import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Constants
BINANCE_API_URL = "https://api.binance.com/api/v3"
KUCOIN_API_URL = "https://api.kucoin.com/api/v1"
MIN_VOLUME = 100  # Minimum trading volume in USDT for a coin to be considered for arbitrage

# Helper functions to get trading pairs for each exchange
def get_binance_pairs(coin):
    url = f"{BINANCE_API_URL}/exchangeInfo"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        available_pairs = []
        for symbol in data["symbols"]:
            if symbol["quoteAsset"] == "USDT" and symbol["status"] == "TRADING":
                if symbol["baseAsset"] == coin:
                    available_pairs.append(symbol["symbol"])
        return available_pairs
    return []

def get_kucoin_pairs(coin):
    url = f"{KUCOIN_API_URL}/market/open/symbols"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        available_pairs = []
        for symbol in data["data"]:
            if symbol["coinType"] == coin and symbol["quoteCurrency"] == "USDT" and symbol["trading"]:
                volume_url = f"{KUCOIN_API_URL}/market/stats?symbol={symbol['symbol']}"
                volume_response = requests.get(volume_url)
                if volume_response.status_code == 200:
                    volume_data = volume_response.json()
                    if volume_data['data']['volValue'] >= MIN_VOLUME:
                        available_pairs.append(symbol["symbol"])
        return available_pairs
    return []

# Main endpoint to get arbitrage opportunities between Binance and Kucoin
@app.route("/arbitrage/<coin>")
def get_arbitrage_opportunities(coin):
    # Get available trading pairs for the specified coin on each exchange
    binance_pairs = get_binance_pairs(coin)
    kucoin_pairs = get_kucoin_pairs(coin)

    # Check for arbitrage opportunities between the two exchanges
    arbitrage_opportunities = []
    for pair in binance_pairs:
        if pair in kucoin_pairs:
            # Get trading fees for the pair on each exchange
            binance_fee_url = f"{BINANCE_API_URL}/ticker/24hr?symbol={pair}"
            binance_fee_response = requests.get(binance_fee_url)
            if binance_fee_response.status_code == 200:
                binance_fee_data = binance_fee_response.json()
                binance_fee = float(binance_fee_data["quoteVolume"]) * float(binance_fee_data["bidPrice"]) * 0.001
            else:
                binance_fee = 0

            kucoin_fee_url = f"{KUCOIN_API_URL}/market/orderbook/level1?symbol={pair}"
            kucoin_fee_response = requests.get(kucoin_fee_url)
            if kucoin_fee_response.status_code == 200:
                kucoin_fee_data = kucoin_fee_response.json()
                kucoin_fee = float(kucoin_fee_data["data"]["bestBid"]) * 0.001
            else:
                kucoin_fee = 0

            # Get coin transfer fees for the specified coin on each exchange
            binance_transfer_fee_url = f"{BINANCE_API_URL}/asset/assetDetail"
            binance_transfer_fee_response = requests.get(binance_transfer_fee_url)
            if binance_transfer_fee_response.status_code == 200:
                binance_transfer_fee_data = binance_transfer_fee_response.json()
                binance_transfer_fee = float(binance_transfer_fee_data[coin]["withdrawFee"])
            else:
                binance_transfer_fee = 0

                kucoin_transfer_fee_url = f"{KUCOIN_API_URL}/wallet/withdraw/fee?currency={coin}"
                kucoin_transfer_fee_response = requests.get(kucoin_transfer_fee_url)
                if kucoin_transfer_fee_response.status_code == 200:
                kucoin_transfer_fee_data = kucoin_transfer_fee_response.json()
                kucoin_transfer_fee = float(kucoin_transfer_fee_data["withdrawMinFee"])
            else:
                kucoin_transfer_fee = 0

            # Calculate potential profit margin for the arbitrage opportunity
            binance_price_url = f"{BINANCE_API_URL}/ticker/price?symbol={pair}"
            binance_price_response = requests.get(binance_price_url)
            kucoin_price_url = f"{KUCOIN_API_URL}/market/orderbook/level1?symbol={pair}"
            kucoin_price_response = requests.get(kucoin_price_url)

            if binance_price_response.status_code == 200 and kucoin_price_response.status_code == 200:
                binance_price_data = binance_price_response.json()
                kucoin_price_data = kucoin_price_response.json()
                binance_price = float(binance_price_data["price"])
                kucoin_price = float(kucoin_price_data["data"]["bestBid"])
                potential_profit_margin = (kucoin_price - binance_price) / binance_price
                # Append the arbitrage opportunity to the list
                arbitrage_opportunities.append({
                    "pair": pair,
                    "binance_fee": binance_fee,
                    "kucoin_fee": kucoin_fee,
                    "binance_transfer_fee": binance_transfer_fee,
                    "kucoin_transfer_fee": kucoin_transfer_fee,
                    "potential_profit_margin": potential_profit_margin
                })

# Sort the arbitrage opportunities by potential profit margin (highest to lowest)
sorted_arbitrage_opportunities = sorted(arbitrage_opportunities, key=lambda x: x["potential_profit_margin"], reverse=True)

# Return the sorted list of arbitrage opportunities as JSON
return jsonify(sorted_arbitrage_opportunities)

