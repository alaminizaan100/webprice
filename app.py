import ccxt
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    exchanges = ccxt.exchanges
    symbols = []
    for exchange_name in exchanges:
        exchange = getattr(ccxt, exchange_name)()
        markets = exchange.load_markets()
        for symbol in markets:
            symbols.append(symbol)
    results = []
    for symbol in symbols:
        for exchange_name in exchanges:
            exchange_buy = getattr(ccxt, exchange_name)()
            exchange_sell = getattr(ccxt, exchange_name)()
            exchange_buy.load_markets()
            exchange_sell.load_markets()
            if symbol in exchange_buy.markets and symbol in exchange_sell.markets:
                if exchange_buy.id != exchange_sell.id:
                    orderbook_buy = exchange_buy.fetch_order_book(symbol)
                    orderbook_sell = exchange_sell.fetch_order_book(symbol)
                    if 'asks' in orderbook_sell and 'bids' in orderbook_buy:
                        buy_price = orderbook_buy['bids'][0][0]
                        sell_price = orderbook_sell['asks'][0][0]
                        transfer_in_fee = exchange_buy.calculate_fee(symbol, 'deposit', 1, 'BTC', 'maker')
                        transfer_out_fee = exchange_sell.calculate_fee(symbol, 'withdraw', 1, 'BTC', 'taker')
                        btc_profit = (sell_price * (1 - transfer_out_fee / 100)) - (buy_price * (1 + transfer_in_fee / 100))
                        usdt_profit = btc_profit * sell_price
                        if usdt_profit > 0:
                            result = {'symbol': symbol, 'exchange_buy': exchange_buy.id, 'exchange_sell': exchange_sell.id, 'btc_profit': btc_profit, 'usdt_profit': usdt_profit}
                            results.append(result)
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
