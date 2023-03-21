import ccxt
import asyncio
from flask import Flask, render_template, Response
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

async def fetch_trades():
    while True:
        trades = {}
        for symbol in exchange.markets:
            channel = f'trade:{symbol}'
            async with exchange.websocket(channel) as ws:
                async for trade in ws:
                    trades[symbol] = trade
        yield trades

@app.route('/')
def index():
    coin_data = asyncio.run(get_all_coin_data())
    return render_template('index.html', coin_data=coin_data)

async def get_all_coin_data():
    tasks = []
    for symbol in exchange.markets:
        tasks.append(asyncio.create_task(get_coin_data(symbol)))
    return await asyncio.gather(*tasks)

async def get_coin_data(symbol):
    ticker = await exchange.fetch_ticker(symbol)
    return {
        'symbol': symbol,
        'last_price': ticker['last'],
        'volume': ticker['quoteVolume'],
        'change': ticker['percentage']
    }

@app.route('/stream')
async def stream():
    async def generate():
        async for trades in fetch_trades():
            yield 'data: {}\n\n'.format(trades)
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
