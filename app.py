import ccxt
import asyncio
from flask import Flask, render_template

app = Flask(__name__)
exchange = ccxt.binance({
    'apiKey': 'OtmdN18Tgx7VjnLyD4Ulc7ooNUaS0ezw38EZtTXvz0Eln4LxePIGCjOC95WG80OG',
    'secret': 'ShmYzH63927bieEp6SgHTDXv3hlEdkiePHMsSpdXpbviKNJbGpPSS6M3YSTACq4u',
    'enableRateLimit': True,
    'options': {
        'websocket': {
            'options': {
                'max_retries': 5,
                'ping_interval': 10,
                'ping_timeout': 5,
                'retry_delay': 2,
                'enableCompression': True,
                'autoReconnect': True,
                'timeout': 20
            }
        }
    }
})
symbols = exchange.load_markets()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trades')
async def trades():
    trades = []

    # Define a coroutine function to handle the websocket subscription
    async def subscribe(channel):
        def callback(trade):
            trades.append(trade)
        await exchange.websocket_subscribe(channel, callback)

    # Use asyncio.gather() to asynchronously subscribe to trade data for each symbol
    await asyncio.gather(*[subscribe(f'trade:{symbol}') for symbol in symbols.keys()[:50]])
    await exchange.websocket_watch()
    return render_template('index.html', trades=trades)


if __name__ == '__main__':
    app.run(debug=True)
