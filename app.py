from flask import Flask, render_template
import ccxt

app = Flask(__name__)

BINANCE = ccxt.binance()
POLONIEX = ccxt.poloniex()

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
            asset_info = BINANCE.fetch_deposit_address(asset)
            if asset_info['info']['success']:
                ticker = BINANCE.fetch_ticker(symbol)
                if ticker['baseVolume'] > 0:
                    filtered_coins[symbol] = {
                        'deposit': asset_info['info']['depositEnable'],
                        'withdraw': asset_info['info']['withdrawEnable'],
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
