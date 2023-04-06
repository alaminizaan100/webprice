


from flask import Flask, render_template
import ccxt

app = Flask(__name__)

@app.route('/')
def index():
    binance = ccxt.binance()
    kucoin = ccxt.kucoin()

    try:
        binance_markets = binance.load_markets()
        binance_spot_markets = {symbol: market for symbol, market in binance_markets.items() if market['spot'] and market['active']}
        binance_tickers = binance.fetch_tickers(list(binance_spot_markets.keys()))
        print("Binance data:", binance_tickers)
    except Exception as e:
        print("Error retrieving data from Binance API:", e)
        binance_tickers = {}

    try:
        kucoin_markets = kucoin.load_markets()
        kucoin_spot_markets = {symbol: market for symbol, market in kucoin_markets.items() if market['spot'] and market['active']}
        kucoin_tickers = kucoin.fetch_tickers(list(kucoin_spot_markets.keys()))
        print("Kucoin data:", kucoin_tickers)
    except Exception as e:
        print("Error retrieving data from Kucoin API:", e)
        kucoin_tickers = {}

    common_symbols = set(binance_tickers.keys()) & set(kucoin_tickers.keys())
    print("Common symbols:", common_symbols)

    data = []
    for symbol in common_symbols:
        binance_price = float(binance_tickers[symbol]['last'])
        kucoin_price = float(kucoin_tickers[symbol]['last'])
        arbitrage = round((kucoin_price - binance_price) / binance_price * 100, 2)
        data.append({
            'symbol': symbol,
            'binance_price': binance_price,
            'kucoin_price': kucoin_price,
            'arbitrage': arbitrage
        })
    print("Data:", data)
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run()


