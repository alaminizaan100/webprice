from flask import Flask
import ccxt.async_support as ccxt
import asyncio

app = Flask(__name__)

# Set up the Binance WebSocket connection
async def binance_ws(symbol):
    exchange = ccxt.binance()
    ticker = await exchange.subscribe_ticker(symbol)
    while True:
        data = await ticker.recv()
        # Convert the price to USD
        price = await exchange.fetch_ticker(symbol)
        usd_price = price['last'] * await exchange.fetch_ticker('BTC/USDT')['last']
        # Print the new ticker data in USD
        print(f'{symbol}: {usd_price}')

# Set up the Flask route and start the WebSocket connection
@app.route('/')
def index():
    symbol = 'BTC/USDT'
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    binance_ws_task = loop.create_task(binance_ws(symbol))
    return 'Binance WebSocket connection started'

if __name__ == '__main__':
    app.run()
