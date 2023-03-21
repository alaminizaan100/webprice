import ccxt.async_support as ccxt
import asyncio
from aiohttp import ClientSession
from flask import Flask, render_template

app = Flask(__name__)
app.config['TIMEOUT'] = 180

async def fetch_ticker(exchange, symbol, session):
    ticker = await exchange.fetch_ticker(symbol)
    return (exchange.id, symbol, ticker['last'])

async def get_tickers(exchange, symbols, session):
    tasks = []
    for symbol in symbols:
        tasks.append(fetch_ticker(exchange, symbol, session))
    results = await asyncio.gather(*tasks)
    return results

async def scan_arbi(exchanges, session):
    symbols = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT']
    tasks = []
    for exchange in exchanges:
        tasks.append(get_tickers(exchange, symbols, session))
    results = await asyncio.gather(*tasks)
    return results

@app.route('/')
async def index():
    async with ClientSession() as session:
        exchanges = [ccxt.binance(), ccxt.bitfinex()]
        results = await scan_arbi(exchanges, session)
    return render_template('index.html', result=results)

if __name__ == '__main__':
    app.run(debug=True)
