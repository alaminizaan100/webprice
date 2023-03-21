from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def binance_data():
    # API endpoint for ticker prices
    url = 'https://api.binance.com/api/v3/ticker/24hr'

    # Make the API request
    response = requests.get(url).json()

    # Create a dictionary to hold the data for each coin
    coins = {}
    for item in response:
        coin = item['symbol'][:-4]
        if coin not in coins:
            coins[coin] = {
                'price': item['lastPrice'],
                'volume': item['volume'],
                'quote': item['quoteVolume']
            }
    
    return render_template('index.html', coins=coins)

if __name__ == '__main__':
    app.run(debug=True)
