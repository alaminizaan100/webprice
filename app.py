


from flask import Flask, render_template
import ccxt

app = Flask(__name__)

@app.route('/')
def index():
    exchanges = {
      #  'binance': ccxt.binance(),
        #'kucoin': ccxt.kucoin(),
        'bittrex': ccxt.bittrex(),
        'poloniex': ccxt.poloniex(),
      #  'kraken': ccxt.kraken(),
     #   'bitfinex': ccxt.bitfinex(),
      #  'bitmex': ccxt.bitmex(),
      #  'coinbasepro': ccxt.coinbasepro(),
      #  'bitstamp': ccxt.bitstamp(),
     #   'gemini': ccxt.gemini(),
     #   'okex': ccxt.okex(),
   #     'huobipro': ccxt.huobipro(),
      #  'hitbtc': ccxt.hitbtc(),
        #'bibox': ccxt.bibox(),
      #  'bithumb': ccxt.bithumb(),
     #   'upbit': ccxt.upbit(),
      #  'gateio': ccxt.gateio(),
       # 'zb': ccxt.zb(),
    #    'lbank': ccxt.lbank(),
       # 'exmo': ccxt.exmo()
    }

    tickers = {}
    for name, exchange in exchanges.items():
        try:
            markets = exchange.load_markets()
            spot_markets = {symbol: market for symbol, market in markets.items() if market['spot'] and market['active']}
            tickers[name] = exchange.fetch_tickers(list(spot_markets.keys()))
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

    print("Data:", data)
    return render_template('index.html', data=data, positive_count=positive_count, negative_count=negative_count)

if __name__ == '__main__':
    app.run()



