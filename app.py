from flask import Flask, render_template
import requests
from operator import itemgetter

app = Flask(__name__)

def get_coins():
    # List of active trading coins
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=24h"
    coins = requests.get(url).json()

    # List of exchanges to fetch coin prices from
    exchanges = ['binance', 'kucoin', 'bitget', 'mexc global', 'bitstamp', 'bitfinex', 'get.io', 'bithumb', 'houbi', 'whitebit', 'exmo']

    result = []
    for coin in coins:
        # Add a new 'prices' key to each coin dictionary
        coin_dict = {}
        coin_dict['prices'] = {}
        for exchange in exchanges:
            # Fetch coin price from the exchange
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin['id']}&vs_currencies={exchange}&include_last_updated_at=true&include_24hr_change=true&include_24hr_vol=true&include_liquidity_rate=true&include_market_cap=true&include_trade_volume_24h=true&include_total_supply=true&include_circulating_supply=true&include_roi=true"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # Add coin price to the 'prices' dictionary for the exchange
                if data.get(coin['id']):
                    coin_dict['prices'][exchange] = data[coin['id']]

        # Remove coins with no active trading markets
        coin_dict['is_active'] = len(coin_dict['prices']) > 0
        if coin_dict['is_active']:
            # Add other keys to the coin dictionary
            coin_dict['id'] = coin['id']
            coin_dict['name'] = coin['name']
            coin_dict['symbol'] = coin['symbol']
            result.append(coin_dict)

    return result

@app.route('/')
def index():
    coins = get_coins()

    for coin in coins:
        # Find the exchange with the lowest and highest coin price
        prices = coin['prices']
        low_exchange = min(prices, key=prices.get)
        high_exchange = max(prices, key=prices.get)

        # Calculate the price difference in percentage
        low_price = prices[low_exchange]
        high_price = prices[high_exchange]
        if low_price == 0:
            percentage_diff = float('inf')
        else:
            percentage_diff = (high_price - low_price) / low_price * 100

        # Add the lowest and highest exchange name and percentage difference to the coin dictionary
        coin['low_exchange'] = low_exchange
        coin['high_exchange'] = high_exchange
        coin['percentage_diff'] = round(percentage_diff, 2)

    # Sort coins by percentage difference
    coins = sorted(coins, key=itemgetter('percentage_diff'), reverse=True)

    return render_template('index.html', coins=coins)


if __name__ == '__main__':
    app.run(debug=True)
