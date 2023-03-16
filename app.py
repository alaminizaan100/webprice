from flask import Flask, render_template
from ccxt.websocket import ConnectionError
import ccxt.async_support as ccxt
import asyncio

app = Flask(__name__)

@app.route('/')
def index():
    # create a new async event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # create a new KuCoin websocket connection
    kucoin_ws = ccxt.kucoin()

    # define the callback function to handle incoming messages
    async def handle_message(message):
        if 'data' in message:
            # extract the price data from the message
            price = message['data']['price']

            # render the price data on the HTML page
            return render_template('index.html', price=price)

    # start the websocket connection
    async def start_websocket():
        try:
            await kucoin_ws.load_markets()
            await kucoin_ws.subscribe('ticker', 'BTC/USDT')
            await kucoin_ws.watch(handle_message)
        except ConnectionError as e:
            print(f"Failed to connect to KuCoin websocket: {e}")

    loop.run_until_complete(start_websocket())

if __name__ == '__main__':
    app.run()
