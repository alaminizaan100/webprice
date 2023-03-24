from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def index():
    pairs = get_trading_pairs()
    triangles = find_triangular_arbitrage(pairs)
    return render_template('index.html', pairs=pairs, triangles=triangles)

def get_trading_pairs():
    response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
    pairs = []
    for symbol in response.json()['symbols']:
        if symbol['status'] == 'TRADING' and (symbol['baseAsset'] == 'BTC' or symbol['baseAsset'] == 'USDT'):
            pairs.append(symbol['symbol'])
    return pairs

def find_triangular_arbitrage(pairs):
    triangles = []
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            for k in range(j + 1, len(pairs)):
                pair1, pair2, pair3 = pairs[i], pairs[j], pairs[k]
                price1 = get_price(pair1)
                price2 = get_price(pair2)
                price3 = get_price(pair3)
                implied_rate = price1 * price2 / price3
                if implied_rate > 1.01:
                    triangles.append((pair1, pair2, pair3, implied_rate))
    return triangles

def get_price(symbol):
    response = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}')
    return float(response.json()['price'])

if __name__ == '__main__':
    app.run(debug=True)
