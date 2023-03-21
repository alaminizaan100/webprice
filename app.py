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
async def fetch_trades():
    global trades
    for symbol in symbols.keys()[:50]:
        channel = f'trade:{symbol}'
        await exchange.websocket_subscribe(channel, lambda t: trades.append(t))

def start_socket():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(fetch_trades())
    loop.run_forever()

@app.route('/')
def index():
    return render_template('index.html', trades=trades)

if __name__ == '__main__':
    socket_thread = Thread(target=start_socket)
    socket_thread.start()
    app.run(debug=True)
