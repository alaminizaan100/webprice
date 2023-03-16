import ccxt
import time
import json

exchange_ids = ['binance', 'kucoin']
symbols = ['BTC/USDT']

exchanges = []
for exchange_id in exchange_ids:
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({
        'enableRateLimit': True,
        'rateLimit': 2000,
    })
    exchange.load_markets()
    exchanges.append(exchange)

for exchange in exchanges:
    for symbol in symbols:
        exchange.subscribe({
            'name': 'ticker',
            'symbol': symbol,
            'interval': '1m'
        })
        time.sleep(0.1)

while True:
    for exchange in exchanges:
        data = exchange.fetch_ticker(symbol)
        if data is not None:
            print(json.dumps(data))
    time.sleep(0.1)
