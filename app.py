import ccxt.async_support as ccxt
import asyncio
from flask import Flask, render_template, Response
import json

app = Flask(__name__)
exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
    'enableRateLimit': True,
})

async def get_top_pairs(n):
    tickers = await exchange.fetch_tickers()
    top_pairs = sorted(tickers, key=lambda k: tickers[k]['quoteVolume'], reverse=True)[:n]
    return top_pairs

async def get_pair_price(pair):
    ticker = await exchange.fetch_ticker(pair)
    return ticker['last']

async def generate():
    top_pairs = await get_top_pairs(100)
    while True:
        prices = {}
        tasks = [asyncio.create_task(get_pair_price(pair)) for pair in top_pairs]
        for i, task in enumerate(asyncio.as_completed(tasks)):
            price = await task
            prices[top_pairs[i]] = price
        yield f"data: {json.dumps(prices)}\n\n"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
async def stream():
    async def generate_with_newline():
        async for prices in generate():
            yield prices + "\n"
    return Response(generate_with_newline(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
