from flask import Flask, render_template
import ccxt

app = Flask(__name__)

@app.route('/')
def home():
    exchanges = ['binance', 'kraken', 'bitfinex', 'coinbase']
    markets = {}
    for exchange in exchanges:
        try:
            ex = getattr(ccxt, exchange)()
            for market in ex.load_markets().values():
                symbol = market['symbol']
                if symbol not in markets:
                    markets[symbol] = {}
                markets[symbol][exchange] = market
        except:
            pass
    return render_template('market_data.html', markets=markets)

if __name__ == '__main__':
    app.run()
