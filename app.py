from flask import Flask, render_template
import ccxt

app = Flask(__name__)

# Initialize Binance and KuCoin exchanges
binance = ccxt.binance()
kucoin = ccxt.kucoin()

@app.route('/')
def index():
    # Get all tickers for Binance and KuCoin
    binance_tickers = binance.fetch_tickers()
    kucoin_tickers = kucoin.fetch_tickers()

    # Get trading fees for Binance and KuCoin
    binance_fees = binance.fetch_trading_fees()
    kucoin_fees = kucoin.fetch_trading_fees()

    # Get withdrawal fees for Binance and KuCoin
    binance_withdrawal_fees = binance.fetch_funding_fees()
    kucoin_withdrawal_fees = kucoin.fetch_funding_fees()

    # Get trading volumes for Binance and KuCoin
    binance_volume = binance.fetch_trading_volume()
    kucoin_volume = kucoin.fetch_trading_volume()

    # Get order book data for BTC/USDT on Binance and KuCoin
    binance_orderbook = binance.fetch_order_book('BTC/USDT')
    kucoin_orderbook = kucoin.fetch_order_book('BTC/USDT')

    return render_template('index.html', 
                           binance_tickers=binance_tickers, 
                           kucoin_tickers=kucoin_tickers,
                           binance_fees=binance_fees,
                           kucoin_fees=kucoin_fees,
                           binance_withdrawal_fees=binance_withdrawal_fees,
                           kucoin_withdrawal_fees=kucoin_withdrawal_fees,
                           binance_volume=binance_volume,
                           kucoin_volume=kucoin_volume,
                           binance_orderbook=binance_orderbook,
                           kucoin_orderbook=kucoin_orderbook)

if __name__ == '__main__':
    app.run(debug=True)
