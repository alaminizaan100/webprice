
import ccxt
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    exchanges = {
        'binance': ccxt.binance({
            'apiKey': 'OtmdN18Tgx7VjnLyD4Ulc7ooNUaS0ezw38EZtTXvz0Eln4LxePIGCjOC95WG80OG',
            'secret': 'ShmYzH63927bieEp6SgHTDXv3hlEdkiePHMsSpdXpbviKNJbGpPSS6M3YSTACq4u'
        }),
        'poloniex': ccxt.poloniex({
            'apiKey': 'T4A9WHNH-LLJONLN7-6EXU0W1Q-YFXFGKUK',
            'secret': '306486a11913376228afebd2717d98fc7d2f6f7557744f52b925ff57a9f03d0eddd09c4c3221fe5acc1a0e3518d1f7c37ec610c7c7d6c3dc1b3628460cb1f001'
        })
    }

    tickers = {}
    volumes = {}
    for name, exchange in exchanges.items():
        try:
            markets = exchange.load_markets()
            currencies = exchange.fetchCurrencies()
            spot_markets = {symbol: market for symbol, market in markets.items() if market['spot'] and market['active']}
            symbols = [symbol for symbol in spot_markets.keys() if currencies[symbol.split('/')[0]]['active'] and currencies[symbol.split('/')[1]]['active']]
            tickers[name] = exchange.fetch_tickers(symbols)
            volumes[name] = {symbol: sum([data[5] for data in exchange.fetch_ohlcv(symbol)]) for symbol in symbols}
            print(f"{name} data:", tickers[name])
        except Exception as e:
            print(f"Error retrieving data from {name} API:", e)
            tickers[name] = {}
            volumes[name] = {}

    data = []
    for symbol in set().union(*[set(t.keys()) for t in tickers.values()]):
        prices = {name: float(t[symbol]['last']) if symbol in t else None for name, t in tickers.items()}
        min_exchange = min(prices, key=lambda k: prices[k] if prices[k] is not None else float('inf'))
        max_exchange = max(prices, key=lambda k: prices[k] if prices[k] is not None else float('-inf'))
        if prices[min_exchange] is not None and prices[max_exchange] is not None:
            arbitrage = round((prices[max_exchange] - prices[min_exchange]) / prices[min_exchange] * 100, 2)
            volume = volumes[max_exchange][symbol]
            data.append({
                'symbol': symbol,
                'min_exchange': min_exchange,
                'min_price': prices[min_exchange],
                'max_exchange': max_exchange,
                'max_price': prices[max_exchange],
                'arbitrage': arbitrage,
                'volume': volume
            })

    # Sort data by arbitrage value
    data.sort(key=lambda x: x['arbitrage'], reverse=True)

    # Count the number of positive and negative arbitrage opportunities
    positive_count = sum(1 for item in data if item['arbitrage'] > 0)
    negative_count = sum(1 for item in data if item['arbitrage'] < 0)

    print("Data:", data)
    return render_template('index.html', data=data, positive_count=positive_count, negative_count=negative_count)

if __name__ == '__main__':
    app.run()
