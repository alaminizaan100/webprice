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

trades = []

def subscribe_to_trades():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async def subscribe(channel):
        def callback(trade):
            trades.append(trade)
        await exchange.websocket_subscribe(channel, callback)
    tasks = [subscribe(f'trade:{symbol}') for symbol in symbols.keys()[:50]]
    loop.run_until_complete(asyncio.gather(*tasks, exchange.websocket_watch()))

@app.route('/')
def index():
    return render_template('index.html', trades=trades)

if __name__ == '__main__':
    t = Thread(target=subscribe_to_trades)
    t.start()
    app.run(debug=True)
