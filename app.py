from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def binance_data():
    # API endpoint for ticker prices
    url = 'https://api.binance.com/api/v3/ticker/24hr'

    # Make the API request
    response = requests.get(url).json()

    # Create a list to hold the data for each coin
    coins = []
    order = 1
    for item in response:
        coin = {
            'order': order,
            'name': item['symbol'][:-4],
            'price': item['lastPrice'],
            'volume': item['volume'],
            'quote': item['quoteVolume']
        }
        coins.append(coin)
        order += 1
    
    num_coins = len(coins)
    return render_template('binance.html', coins=coins, num_coins=num_coins)

if __name__ == '__main__':
    app.run(debug=True)
