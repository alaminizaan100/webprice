
from flask import Flask, render_template
import requests

app = Flask(__name__)

BINANCE_API_KEY = 'xhWaoPZeD5RSaHqkqyUR6m3UPgiSIjDjEy1j5dMQXdAWFUafVKnSKbss1FIJRufh'
BINANCE_API_SECRET = '68JZbq7X0UqjTFd42aduFio3JbK3QlYHeQBLANw03RdV6QCNu0OHT9xDkCGiLFTf'
POLONIEX_API_KEY = 'T4A9WHNH-LLJONLN7-6EXU0W1Q-YFXFGKUK'
POLONIEX_API_SECRET = '306486a11913376228afebd2717d98fc7d2f6f7557744f52b925ff57a9f03d0eddd09c4c3221fe5acc1a0e3518d1f7c37ec610c7c7d6c3dc1b3628460cb1f001'

BINANCE_BASE_URL = 'https://api.binance.com'
POLONIEX_BASE_URL = 'https://poloniex.com/public'

@app.route('/')
def index():
    # Load markets
    binance_markets = requests.get(f'{BINANCE_BASE_URL}/api/v3/exchangeInfo').json()
    poloniex_markets = requests.get(f'{POLONIEX_BASE_URL}?command=returnTicker').json()

    # Filter coins based on deposit, trading, withdrawal status and volume
    filtered_coins = {}
    for symbol in binance_markets['symbols']:
        if symbol['status'] == 'TRADING':
            asset = symbol['baseAsset']
            asset_info = requests.get(f'{BINANCE_BASE_URL}/sapi/v1/asset/assetDetail?asset={asset}', headers={'X-MBX-APIKEY': BINANCE_API_KEY}).json()
            if asset_info[asset]['depositStatus'] and asset_info[asset]['withdrawStatus']:
                ticker = requests.get(f'{BINANCE_BASE_URL}/api/v3/ticker/24hr?symbol={symbol["symbol"]}').json()
                if float(ticker['quoteVolume']) > 0:
                    filtered_coins[symbol['symbol']] = {
                        'deposit': asset_info[asset]['depositStatus'],
                        'withdraw': asset_info[asset]['withdrawStatus'],
                        'volume': float(ticker['quoteVolume'])
                    }

    # Store coin withdrawal fee and trading fee
    fees = {}
    for symbol in filtered_coins:
        asset = symbol.split('/')[0]
        withdrawal_fees = requests.get(f'{BINANCE_BASE_URL}/sapi/v1/asset/assetDetail', headers={'X-MBX-APIKEY': BINANCE_API_KEY}).json()
        fees[symbol] = {
            'withdrawal_fee': withdrawal_fees[asset]['withdrawFee'],
            'binance_trading_fee': 0.1,
            'poloniex_trading_fee': 0.2
        }

    # Calculate arbitrage opportunities
    opportunities = []
    for symbol in filtered_coins:
        binance_price = float(requests.get(f'{BINANCE_BASE_URL}/api/v3/ticker/price?symbol={symbol}').json()['price'])
        poloniex_symbol = f'{symbol.split("/")[1]}_{symbol.split("/")[0]}'
        if poloniex_symbol in poloniex_markets:
            poloniex_price = float(poloniex_markets[poloniex_symbol]['last'])
            arbitrage = (poloniex_price - binance_price) / binance_price * 100
            # Deduct trading fee and coin transfer fee
            arbitrage -= fees[symbol]['binance_trading_fee'] + fees[symbol]['poloniex_trading_fee'] + fees[symbol]['withdrawal_fee']
            opportunities.append({
                'symbol': symbol,
                'arbitrage': arbitrage,
                'volume': filtered_coins[symbol]['volume'],
                'deposit': filtered_coins[symbol]['deposit'],
                'trade': True,
                'withdraw': filtered_coins[symbol]['withdraw']
            })

    return render_template('index.html', opportunities=opportunities)

if __name__ == '__main__':
    app.run()
