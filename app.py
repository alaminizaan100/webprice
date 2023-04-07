from flask import Flask, render_template
import ccxt

app = Flask(__name__)

BINANCE_API_KEY = 'xhWaoPZeD5RSaHqkqyUR6m3UPgiSIjDjEy1j5dMQXdAWFUafVKnSKbss1FIJRufh'
BINANCE_API_SECRET = '68JZbq7X0UqjTFd42aduFio3JbK3QlYHeQBLANw03RdV6QCNu0OHT9xDkCGiLFTf'
POLONIEX_API_KEY = 'T4A9WHNH-LLJONLN7-6EXU0W1Q-YFXFGKUK'
POLONIEX_API_SECRET = '306486a11913376228afebd2717d98fc7d2f6f7557744f52b925ff57a9f03d0eddd09c4c3221fe5acc1a0e3518d1f7c37ec610c7c7d6c3dc1b3628460cb1f001'

BINANCE = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET
})
POLONIEX = ccxt.poloniex({
    'apiKey': POLONIEX_API_KEY,
    'secret': POLONIEX_API_SECRET
})

@app.route('/')
def index():
    # Load markets
    binance_markets = BINANCE.load_markets()
    poloniex_markets = POLONIEX.load_markets()

    # Filter coins based on deposit, trading, withdrawal status and volume
    filtered_coins = {}
    for symbol in binance_markets:
        market = binance_markets[symbol]
        if market['active'] and market['info']['status'] == 'TRADING':
            asset = symbol.split('/')[0]
            asset_info = BINANCE.sapi_get_asset_detail(params={'asset': asset})
            if asset_info['depositStatus'] and asset_info['withdrawStatus']:
                ticker = BINANCE.fetch_ticker(symbol)
                if ticker['baseVolume'] > 0:
                    filtered_coins[symbol] = {
                        'deposit': asset_info['depositStatus'],
                        'withdraw': asset_info['withdrawStatus'],
                        'volume': ticker['baseVolume']
                    }

    # Store coin withdrawal fee and trading fee
    fees = {}
    for symbol in filtered_coins:
        asset = symbol.split('/')[0]
        fees[symbol] = {
            'withdrawal_fee': BINANCE.fetch_withdrawal_fees()[asset],
            'binance_trading_fee': 0.1,
            'poloniex_trading_fee': 0.2
        }

    # Calculate arbitrage opportunities
    opportunities = []
    for symbol in filtered_coins:
        binance_price = BINANCE.fetch_ticker(symbol)['last']
        poloniex_symbol = f'{symbol.split("/")[1]}_{symbol.split("/")[0]}'
        if poloniex_symbol in poloniex_markets:
            poloniex_price = POLONIEX.fetch_ticker(poloniex_symbol)['last']
            arbitrage = (poloniex_price - binance_price) / binance_price * 100
            # Deduct trading fee and coin transfer fee
            arbitrage -= fees[symbol]['binance_trading_fee'] + fees[symbol]['poloniex_trading_fee'] + fees[symbol]['withdrawal_fee']
            opportunities.append({
                'symbol': symbol,
                'arbitrage': arbitrage,
                'volume': filtered_coins[symbol]['volume'],
                'deposit': filtered_coins[symbol]['deposit'],
                'trade': market['active'],
                'withdraw': filtered_coins[symbol]['withdraw']
            })

    return render_template('index.html', opportunities=opportunities)

if __name__ == '__main__':
    app.run()
