import ccxt
import asyncio
from flask import Flask, render_template
from threading import Thread

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

trades = {}

async def fetch_trades():
    global trades
    for symbol in symbols.keys():
        channel = f'trade:{symbol}'
        await exchange.websocket_subscribe(channel, lambda t: trades.update({symbol: t}))

async def start_socket():
    await asyncio.run(fetch_trades())

@app.route('/')
def index():
    coin_data = []
    for symbol in list(symbols.keys()):
        coin_data.append(get_coin_data(symbol))
    return render_template('index.html', coin_data=coin_data)

@app.route('/stream')
def stream():
    async def generate():
        while True:
            yield 'data: {}\n\n'.format(trades)
            trades.clear()
            await asyncio.sleep(1)
    return app.response_class(generate(), mimetype='text/event-stream')

def get_coin_data(symbol):
    ticker = exchange.fetch_ticker(symbol)
    return {
        'symbol': symbol,
        'last_price': ticker['last'],
        'volume': ticker['quoteVolume'],
        'change': ticker['percentage']
    }

if __name__ == '__main__':
    asyncio.run(start_socket())
    app.run(debug=True)
