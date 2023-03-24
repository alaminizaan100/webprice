from flask import Flask, render_template
from binance.client import Client

app = Flask(__name__)
client = Client()

@app.route('/')
def index():
    pairs = get_active_pairs()
    triangles = find_triangular_arbitrage(pairs)
    return render_template('index.html', pairs=pairs, triangles=triangles)

def get_active_pairs():
    pairs = []
    tickers = client.get_all_tickers()
    for ticker in tickers:
        symbol = ticker['symbol']
        if symbol.endswith('BTC') or symbol.endswith('USDT'):
            pairs.append(symbol)
    return pairs

def find_triangular_arbitrage(pairs):
    triangles = []
    for pair1 in pairs:
        for pair2 in pairs:
            if pair1 == pair2:
                continue
            for pair3 in pairs:
                if pair3 == pair1 or pair3 == pair2:
                    continue
                if check_arbitrage_opportunity(pair1, pair2, pair3):
                    triangles.append((pair1, pair2, pair3))
    return triangles

def check_arbitrage_opportunity(pair1, pair2, pair3):
    # TODO: Implement triangular arbitrage check using Binance API
    # For example, use client.get_order_book(symbol=pair1) to retrieve the order book
    return False

if __name__ == '__main__':
    app.run(debug=True)
