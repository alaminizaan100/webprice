from flask import Flask, render_template

import requests

app = Flask(__name__)

@app.route('/')

def index():

    binance_url = "https://api.binance.com/api/v3/ticker/price"

    kucoin_url = "https://api.kucoin.com/api/v1/market/allTickers"

    binance_response = requests.get(binance_url)

    kucoin_response = requests.get(kucoin_url)

    binance_data = binance_response.json()

    kucoin_data = kucoin_response.json()['data']['ticker']

    binance_prices = {item['symbol']: float(item['price']) for item in binance_data}

    kucoin_prices = {item['symbol']: float(item['last']) for item in kucoin_data}

    common_symbols = set(binance_prices.keys()) & set(kucoin_prices.keys())

    data = []

    for symbol in common_symbols:

        binance_price = binance_prices[symbol]

        kucoin_price = kucoin_prices[symbol]

        arbitrage = round((kucoin_price - binance_price) / binance_price * 100, 2)

        data.append({

            'symbol': symbol,

            'binance_price': binance_price,

            'kucoin_price': kucoin_price,

            'arbitrage': arbitrage

        })
    print(data)
    return render_template('index.html', data=data)

if __name__ == '__main__':

    app.run()

