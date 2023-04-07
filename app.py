


from flask import Flask, render_template
import aiohttp
import asyncio
import requests

app = Flask(__name__)

BINANCE_API_URL = 'https://api.binance.com/api/v3/ticker/price'
POLONIEX_API_URL = 'https://poloniex.com/public?command=returnTicker'

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def get_data():
    async with aiohttp.ClientSession() as session:
        binance_prices = await fetch(session, BINANCE_API_URL)
        poloniex_prices = await fetch(session, POLONIEX_API_URL)
        return binance_prices, poloniex_prices

@app.route('/')
def index():
    binance_prices, poloniex_prices = asyncio.run(get_data())

    # Filter coins based on deposit, trading, withdrawal status and volume
    filtered_coins = []
    for coin in binance_prices:
        symbol = coin['symbol']
        asset = symbol[:-3]
        asset_info = requests.get(f'https://api.binance.com/api/v3/assetDetail?asset={asset}').json()
        if asset_info['depositStatus'] and asset_info['withdrawStatus'] and asset_info['tradingStatus']:
            volume = float(requests.get(f'https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}').json()['volume'])
            if volume > 0:
                filtered_coins.append(symbol)

    # Calculate arbitrage opportunities
    opportunities = []
    for symbol in filtered_coins:
        binance_price = float(next(item for item in binance_prices if item['symbol'] == symbol)['price'])
        poloniex_symbol = f'{symbol[-3:]}_{symbol[:-3]}'
        if poloniex_symbol in poloniex_prices:
            poloniex_price = float(poloniex_prices[poloniex_symbol]['last'])
            arbitrage = (poloniex_price - binance_price) / binance_price * 100
            # Deduct trading fee (0.1%) and coin transfer fee
            arbitrage -= 0.1
            opportunities.append({'symbol': symbol, 'arbitrage': arbitrage})

    return render_template('index.html', opportunities=opportunities)

if __name__ == '__main__':
    app.run()

    

