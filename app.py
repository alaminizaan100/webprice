# Import necessary libraries
from flask import Flask, render_template
import requests

# Create Flask application
app = Flask(__name__)

# Define a route to display the prices
@app.route('/prices')
def display_prices():
    # Define a dictionary to store the prices from all 10 exchanges
    prices = {}

    # Define a list of tuples with the exchange name and its API endpoint
    exchanges = [
        ('Binance', 'https://api.binance.com/api/v3/ticker/price'),
        ('Bitfinex', 'https://api.bitfinex.com/v1/pubticker/all'),
        ('Bitstamp', 'https://www.bitstamp.net/api/v2/ticker_hour/'),
        ('Coinbase Pro', 'https://api.pro.coinbase.com/products/ticker'),
        ('Kraken', 'https://api.kraken.com/0/public/Ticker'),
        ('Huobi', 'https://api.huobi.pro/market/tickers'),
        ('OKEx', 'https://www.okex.com/api/spot/v3/instruments/ticker'),
        ('Upbit', 'https://api.upbit.com/v1/ticker'),
        ('Bithumb', 'https://api.bithumb.com/public/ticker/all'),
        ('Bitflyer', 'https://api.bitflyer.com/v1/getticker'),
    ]

    # Loop through each exchange and extract the prices for all available trading coins
    for exchange, endpoint in exchanges:
        response = requests.get(endpoint)
        data = response.json()

        # Extract the prices for all available trading coins
        if exchange == 'Binance':
            for coin in data:
                symbol = coin['symbol']
                price = float(coin['price'])
                prices[f"{exchange} - {symbol}"] = price
        elif exchange == 'Bitfinex':
            for coin, info in data.items():
                symbol = coin.upper()
                price = float(info['last_price'])
                prices[f"{exchange} - {symbol}"] = price
        elif exchange == 'Bitstamp':
            for coin, info in data.items():
                symbol = coin.upper()
                price = float(info['last'])
                prices[f"{exchange} - {symbol}"] = price
        elif exchange == 'Coinbase Pro':
            for coin in data:
                symbol = coin['product_id'].replace('-', '/')
                price = float(coin['price'])
                prices[f"{exchange} - {symbol}"] = price
        elif exchange == 'Kraken':
            for symbol, info in data['result'].items():
                price = float(info['c'][0])
                prices[f"{exchange} - {symbol}"] = price
        elif exchange == 'Huobi':
            for coin in data['data']:
                symbol = coin['symbol'].replace('_', '/')
                price = float(coin['close'])
                prices[f"{exchange} - {symbol}"] = price
        elif exchange == 'OKEx':
            for coin in data:
                symbol = coin['instrument_id'].replace('-', '/')
                price = float(coin['last'])
                prices[f"{exchange} - {symbol}"] = price
        elif exchange == 'Upbit':
            for coin in data:
                symbol = coin['market'].replace('-', '/')
                price = float(coin['trade_price'])
                prices[f"{exchange} - {symbol}
                elif exchange == 'Bithumb':
            for coin, info in data['data'].items():
                symbol = coin.replace('_', '/')
                price = float(info['closing_price'])
                prices[f"{exchange} - {symbol}"] = price
        elif exchange == 'Bitflyer':
            for coin in data:
                symbol = coin['product_code'].replace('_', '/')
                price = float(coin['ltp'])
                prices[f"{exchange} - {symbol}"] = price

    # Render the HTML template with the prices
    return render_template('prices.html', prices=prices)
