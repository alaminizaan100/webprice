


from flask import Flask, render_template
import asyncio
import ccxt.async_support as ccxt

app = Flask(__name__)

async def fetch_tickers(exchange):
    try:
        markets = await exchange.load_markets()
        spot_markets = {symbol: market for symbol, market in markets.items() if market['spot'] and market['active']}
        tickers = await exchange.fetch_tickers(list(spot_markets.keys()))
        return tickers
    except Exception as e:
        print(f"Error retrieving data from {exchange.name} API:", e)
        return {}

@app.route('/')
async def index():
    exchanges = {
        'binance': ccxt.binance(),
        'kucoin': ccxt.kucoin(),
        'bittrex': ccxt.bittrex(),
        'poloniex': ccxt.poloniex(),
    }

    tasks = [fetch_tickers(exchange) for exchange in exchanges.values()]
    results = await asyncio.gather(*tasks)

    tickers = dict(zip(exchanges.keys(), results))

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

    return render_template('index.html', data=data, positive_count=positive_count, negative_count=negative_count)

if __name__ == '__main__':
    app.run()
