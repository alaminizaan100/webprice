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
            if asset_info.get(asset, {}).get('depositStatus', False) and asset_info.get(asset, {}).get('withdrawStatus', False):
                ticker = requests.get(f'{BINANCE_BASE_URL}/api/v3/ticker/24hr?symbol={symbol["symbol"]}').json()
                if float(ticker.get('quoteVolume', 0)) > 0:
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
            'withdrawal_fee': withdrawal_fees.get(asset, {}).get('withdrawFee', 0),
            'binance_trading_fee': 0.1,
            'poloniex_trading_fee': 0.2
        }

    # Calculate arbitrage opportunities
    # Calculate arbitrage opportunities
    opportunities = []
    for symbol in filtered_coins:
    binance_price = float(requests.get(f'{BINANCE_BASE_URL}/api/v3/ticker/price?symbol={symbol}').json()['price'])
    poloniex_symbol = f'{symbol.split("/")[1]}_{symbol.split("/")[0]}'
    if poloniex_symbol in poloniex_markets:
        poloniex_price = float(poloniex_markets[poloniex_symbol]['last'])
        binance_min_notional = float(requests.get(f'{BINANCE_BASE_URL}/api/v3/exchangeInfo?symbol={symbol}').json()['filters'][3]['minNotional'])
        poloniex_min_trade_size = float(requests.get(f'{POLONIEX_BASE_URL}?command=returnTicker')[poloniex_symbol]['lowestAsk']) # change BTC_ETH to poloniex_symbol
        # Determine minimum trade size
        if binance_min_notional / binance_price < poloniex_min_trade_size:
            min_trade_size = poloniex_min_trade_size
        else:
            min_trade_size = binance_min_notional / binance_price
        # Determine maximum trade size
        max_trade_size = min(filtered_coins[symbol]['volume'], 10 * min_trade_size)  # Arbitrage up to 10 times minimum trade size
        # Calculate potential arbitrage profit
        arbitrage = (poloniex_price - binance_price) / binance_price * 100
        # Deduct trading fees, transfer fees, and minimum trade size
        arbitrage -= fees[symbol]['binance_trading_fee'] + fees[symbol]['poloniex_trading_fee'] + fees[symbol]['withdrawal_fee']
        # Filter opportunities with negative or too small arbitrage
        if arbitrage > 0 and arbitrage > min_arbitrage and max_trade_size > min_trade_size:
            opportunities.append({
                'symbol': symbol,
                'arbitrage': arbitrage,
                'volume': filtered_coins[symbol]['volume'],
                'deposit': filtered_coins[symbol]['deposit'],
                'trade': True,
                'withdraw': filtered_coins[symbol]['withdraw'],
                'min_trade_size': min_trade_size,
                'max_trade_size': max_trade_size
            })

return render_template('index.html', opportunities=opportunities)
if __name__ == '__main__':
    app.run()
