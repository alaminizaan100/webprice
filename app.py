from flask import Flask, render_template
import requests

app = Flask(__name__)

# List of API endpoints for ticker prices
ticker_urls = [
    'https://api.binance.com/api/v3/ticker/price',
    'https://api.bitfinex.com/v1/pubticker/all',
    # Add more exchange endpoints here
]

# List of API endpoints for exchange information
info_urls = [
    'https://api.binance.com/api/v3/exchangeInfo',
    'https://api.bitfinex.com/v1/symbols_details',
    # Add more exchange endpoints here
]

# Trading fee as decimal
trading_fee = 0.001

@app.route('/')
def binance_data():
    opportunities = []
    for i in range(len(ticker_urls)):
        # Make the API requests
        ticker_response = requests.get(ticker_urls[i]).json()
        info_response = requests.get(info_urls[i]).json()

        # Fetch USDT price
        usdt_price = 1.0
        if 'USDT' in ticker_response:
            usdt_price = float(ticker_response['USDT']['last_price'])

        # Create a dictionary of asset names for spot trading
        asset_names = {}
        for asset in info_response:
            if asset['status'] != 'TRADING':
                continue
            asset_names[asset['symbol']] = {
                'base': asset['base'],
                'quote': asset['quote']
            }

        # Create a dictionary to hold the data for each coin
        coins = {}
        for symbol in ticker_response:
            if symbol not in asset_names:
                continue
            base_asset = asset_names[symbol]['base']
            quote_asset = asset_names[symbol]['quote']
            price = float(ticker_response[symbol]['last_price'])
            if base_asset not in coins:
                coins[base_asset] = {}
            coins[base_asset][quote_asset] = price

        # Find triangular arbitrage opportunities
        for base_asset in coins:
            for quote_asset_1 in coins[base_asset]:
                if quote_asset_1 not in coins:
                    continue
                for quote_asset_2 in coins[quote_asset_1]:
                    if quote_asset_2 not in coins:
                        continue
                    if base_asset in coins[quote_asset_2]:
                        rate_1 = coins[base_asset][quote_asset_1] * (1 - trading_fee)
                        rate_2 = coins[quote_asset_1][quote_asset_2] * (1 - trading_fee)
                        rate_3 = coins[quote_asset_2][base_asset] * (1 - trading_fee)
                        opportunity = {
                            'exchange': i+1,
                            'base_asset': base_asset,
                            'quote_asset_1': quote_asset_1,
                            'quote_asset_2': quote_asset_2,
                            'rate_1': rate_1,
                            'rate_2': rate_2,
                            'rate_3': rate_3,
                            'potential_profit': round(rate_1 * rate_2 * rate_3 - 1, 4),
                            'potential_profit_usdt': round((rate_1 * rate_2 * rate_3 - 1) * usdt_price, 4)
                        }
                        opportunities.append(opportunity)

    opportunities = sorted(opportunities, key=lambda x: x['potential_profit'], reverse=True)

    num_opportunities = len(op
