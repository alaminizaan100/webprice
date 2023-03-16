from flask import Flask, jsonify
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
            return jsonify({'exchange': 'Binance', 'pair': 'BTC/USDT', 'price': binance_price})

    @kucoin.on('ticker')
    async def kucoin_ticker_update(ticker, client):
        if ticker['symbol'] == 'BTC/USDT':
            kucoin_price = ticker['last']
            print(f'KuCoin BTC/USDT price: {kucoin_price}')
            return jsonify({'exchange': 'KuCoin', 'pair': 'BTC/USDT', 'price': kucoin_price})

    binance.start()
    kucoin.start()

if __name__ == '__main__':
    app.run()
