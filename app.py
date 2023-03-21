from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def binance_data():
    # API endpoint for ticker prices
    ticker_url = 'https://api.binance.com/api/v3/ticker/24hr'
    # API endpoint for exchange information
    info_url = 'https://api.binance.com/api/v3/exchangeInfo'

    # Make the API requests
    ticker_response = requests.get(ticker_url).json()
    info_response = requests.get(info_url).json()

    # Create a dictionary of asset names
    asset_names = {}
    for asset in info_response['symbols']:
        asset_names[asset['symbol']] = {
            'base': asset['baseAsset'],
            'quote': asset['quoteAsset']
        }

    # Create a list to hold the data for each coin
    coins = []
    order = 1
    for item in ticker_response:
        symbol = item['symbol']
        coin = {
            'order': order,
            'symbol': symbol,
            'name': asset_names[symbol]['base'] + '/' + asset_names[symbol]['quote'],
            'price': item['lastPrice'],
            'volume': item['volume'],
            'quote': item['quoteVolume']
        }
        coins.append(coin)
        order += 1
    
    num_coins = len(coins)
    return render_template('index.html', coins=coins, num_coins=num_coins)

if __name__ == '__main__':
    app.run(debug=True)
