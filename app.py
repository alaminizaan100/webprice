


from flask import Flask, render_template
import ccxt

app = Flask(__name__)

@app.route('/')
def index():
    exchanges = {
        'binance': ccxt.binance(),
        'kucoin': ccxt.kucoin(),
        'poloniex': ccxt.poloniex()
    }

    filtered_symbols = {}
    for name, exchange in exchanges.items():
        try:
            currencies = exchange.fetch_currencies()
            active_currencies = {code: currency for code, currency in currencies.items() if currency['active'] and currency['deposit'] and currency['withdrawal']}
            markets = exchange.load_markets()
            spot_markets = {symbol: market for symbol, market in markets.items() if market['spot'] and market['active']}
            filtered_symbols[name] = [symbol for symbol in spot_markets.keys() if symbol.split('/')[0] in active_currencies and symbol.split('/')[1] in active_currencies]
        except Exception as e:
            print(f"Error retrieving data from {name} API:", e)
            filtered_symbols[name] = []

    tickers = {}
    for name, exchange in exchanges.items():
        try:
            tickers[name] = exchange.fetch_tickers(filtered_symbols[name])
            print(f"{name} data:", tickers[name])
        except Exception as e:
            print(f"Error retrieving data from {name} API:", e)
            tickers[name] = {}

    data = []
    for symbol in set().union(*[set(t.keys()) for t in tickers.values()]):
        prices = {name: float(t[symbol]['last']) if symbol in t else None for name, t in tickers.items()}
        min_exchange = min(prices, key=lambda k: prices[k] if prices[k] is not None else float('inf'))
        max_exchange = max(prices, key=lambda k: prices[k] if prices[k] is not None else float('-inf'))
        if prices[min_exchange] is not None and prices[max_exchange] is not None:
            arbitrage = round((prices[max_exchange] - prices[min_exchange]) / prices[min_exchange] * 100, 2)
            data.append({
                'symbol': symbol,
                'min_exchange': min_exchange,
                'min_price': prices[min_exchange],
                'max_exchange': max_exchange,
                'max_price': prices[max_exchange],
                'arbitrage': arbitrage
            })

    # Sort data by arbitrage value
    data.sort(key=lambda x: x['arbitrage'], reverse=True)

    # Count the number of positive and negative arbitrage opportunities
    positive_count = sum(1 for item in data if item['arbitrage'] > 0)
    negative_count = sum(1 for item in data if item['arbitrage'] < 0)

    print(active_currencies)
    return render_template('index.html', data=data, positive_count=positive_count, negative_count=negative_count)

if __name__ == '__main__':
    app.run()


