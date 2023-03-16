from flask import Flask, jsonify, render_template
import ccxtpro

app = Flask(__name__)

@app.route('/')
def index():
    binance = ccxtpro.binance({
        'enableRateLimit': True,
    })
    kucoin = ccxtpro.kucoin({
        'enableRateLimit': True,
    })

    binance.subscribe('ticker', 'BTC/USDT')
    kucoin.subscribe('ticker', 'BTC/USDT')

    @binance.on('ticker')
    async def binance_ticker_update(ticker, client):
        if ticker['symbol'] == 'BTC/USDT':
            binance_price = ticker['last']
            print(f'Binance BTC/USDT price: {binance_price}')
            return binance_price

    @kucoin.on('ticker')
    async def kucoin_ticker_update(ticker, client):
        if ticker['symbol'] == 'BTC/USDT':
            kucoin_price = ticker['last']
            print(f'KuCoin BTC/USDT price: {kucoin_price}')
            return kucoin_price

    binance.start()
    kucoin.start()

    binance_price = binance.fetch_ticker('BTC/USDT')['last']
    kucoin_price = kucoin.fetch_ticker('BTC/USDT')['last']
    return render_template('index.html', binance_price=binance_price, kucoin_price=kucoin_price)

if __name__ == '__main__':
    app.run()
