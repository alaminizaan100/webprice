from flask import Flask, render_template
import requests

app = Flask(__name__)

# Binance API endpoints
api_base_url = "https://api.binance.com"
ticker_price_endpoint = "/api/v3/ticker/price"
exchange_info_endpoint = "/api/v3/exchangeInfo"
ticker_24h_endpoint = "/api/v3/ticker/24hr"
depth_endpoint = "/api/v3/depth"

@app.route('/')
def index():
    # Retrieve all ticker prices
    ticker_prices = requests.get(api_base_url + ticker_price_endpoint).json()

    # Retrieve exchange info
    exchange_info = requests.get(api_base_url + exchange_info_endpoint).json()

    # Retrieve 24-hour ticker statistics for all symbols
    ticker_24h_stats = requests.get(api_base_url + ticker_24h_endpoint).json()

    # Check if ticker_24h_stats is a list
    if not isinstance(ticker_24h_stats, list):
        # If it's not a list, try to extract the relevant data from the dictionary
        ticker_24h_stats = [ticker_24h_stats[symbol] for symbol in ticker_24h_stats]

    # Parse exchange info to extract symbol and base asset info
    symbols = {}
    for symbol in exchange_info['symbols']:
        if symbol['status'] == "TRADING":
            symbol_name = symbol['symbol']
            base_asset = symbol['baseAsset']
            quote_asset = symbol['quoteAsset']
            symbols[symbol_name] = {'base_asset': base_asset, 'quote_asset': quote_asset}

    # Combine ticker prices and 24h stats with symbol and asset info
    data = []
    for ticker in ticker_prices:
        symbol = ticker['symbol']
        if symbol in symbols:
            # Retrieve the 24h stats for the symbol
            symbol_24h_stats = None
            for stats in ticker_24h_stats:
                if stats['symbol'] == symbol:
                    symbol_24h_stats = stats
                    break
            
            if symbol_24h_stats:
                data.append({
                    'symbol': symbol,
                    'base_asset': symbols[symbol]['base_asset'],
                    'quote_asset': symbols[symbol]['quote_asset'],
                    'price': ticker['price'],
                    '24h_volume': symbol_24h_stats['volume'],
                    '24h_change': symbol_24h_stats['priceChangePercent'],
                    'withdraw_fee': symbol in exchange_info['withdrawFee'],
                    'trading_fee': exchange_info['rateLimits'][0]['rate'] / 10000
                })

    # Retrieve order book for all trading symbols
    depth_data = {}
    for symbol in symbols.keys():
        depth = requests.get(api_base_url + depth_endpoint, params={'symbol': symbol}).json()
        bids = depth['bids']
        asks = depth['asks']
        depth_data[symbol] = {'bids': bids, 'asks': asks}

    # Render HTML template with data
    return render_template('index.html', data=data, depth_data=depth_data)

if __name__ == '__main__':
    app.run(debug=True)
