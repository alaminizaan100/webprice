from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def binance_data():
    # API endpoint for ticker prices
    ticker_url = 'https://api.binance.com/api/v3/ticker/price'
    # API endpoint for spot exchange information
    info_url = 'https://api.binance.com/api/v3/exchangeInfo'
    # Trading fee as decimal
    trading_fee = 0.001

    # Make the API requests
    print('Fetching ticker data...')
    ticker_response = requests.get(ticker_url).json()
    print(f'Ticker data retrieved for {len(ticker_response)} assets.')
    print('Fetching spot exchange information...')
    info_response = requests.get(info_url).json()
    print(f'Exchange information retrieved for {len(info_response["symbols"])} assets.')

    # Fetch USDT price
    usdt_price = 1.0
    for item in ticker_response:
        if item['symbol'] == 'USDTBUSD':
            usdt_price = float(item['price'])
            break
    print(f'USDT price retrieved: {usdt_price}')

    # Create a dictionary of asset names for spot trading
    asset_names = {}
    for asset in info_response['symbols']:
        if asset['status'] != 'TRADING':
            continue
        asset_names[asset['symbol']] = {
            'base': asset['baseAsset'],
            'quote': asset['quoteAsset']
        }
    print(f'{len(asset_names)} assets available for trading.')

    # Create a dictionary to hold the data for each coin
    coins = {}
    for item in ticker_response:
        symbol = item['symbol']
        if symbol not in asset_names:
            continue
        base_asset = asset_names[symbol]['base']
        quote_asset = asset_names[symbol]['quote']
        price = float(item['price'])
        if base_asset not in coins:
            coins[base_asset] = {}
        coins[base_asset][quote_asset] = price
    print(f'{len(coins)} base assets and {sum(len(v) for v in coins.values())} quote assets available for trading.')

    # Convert all assets to USDT
    for base_asset in coins:
        if base_asset != 'USDT':
            if 'USDT' in coins[base_asset]:
                rate = coins[base_asset]['USDT']
                coins[base_asset]['USDT'] = 1 / rate
            else:
                for quote_asset in coins[base_asset]:
                    rate = coins[base_asset][quote_asset] * coins[quote_asset]['USDT']
                    coins[base_asset][quote_asset] = 1 / rate

    # Find triangular arbitrage opportunities
    opportunities = []
for base_asset in coins:
    for quote_asset_1 in coins[base_asset]:
        if quote_asset_1 not in coins:
            continue
        for quote_asset_2 in coins[quote_asset_1]:
            if quote_asset_2 not in coins:
                continue
            if base_asset in coins[quote_asset_2]:
                rate_1 = coins[base_asset][quote_asset_1] * (1 - trading_fee)
                rate_2 = coins[quote_asset_1][quote_asset_2] * (1 - trading_fee)
                rate_3 = coins[quote_asset_2][base_asset] * (1 - trading_fee)
                potential_profit = rate_1 * rate_2 * rate_3
                
                # Print arbitrage calculation data
                print(f"Buy {base_asset} with {quote_asset_1} at {coins[base_asset][quote_asset_1]}")
                print(f"Sell {quote_asset_1} for {quote_asset_2} at {coins[quote_asset_1][quote_asset_2]}")
                print(f"Sell {quote_asset_2} for {base_asset} at {coins[quote_asset_2][base_asset]}")
                print(f"Potential profit: {potential_profit - 1:.5f}")
                print("-----")
                
                if potential_profit > 1:
                    opportunities.append({
                        'buy': base_asset,
                        'sell': quote_asset_1,
                        'exchange': quote_asset_2,
                        'profit': potential_profit - 1,
                        'rate_1': rate_1,
                        'rate_2': rate_2,
                        'rate_3': rate_3,
                        'price_1': coins[base_asset][quote_asset_1],
                        'price_2': coins[quote_asset_1][quote_asset_2],
                        'price_3': coins[quote_asset_2][base_asset]
                    })

# Sort the opportunities by profit
opportunities.sort(key=lambda x: x['profit'], reverse=True)

# Render the HTML page with some important data
return render_template('index.html', opportunities=opportunities, trading_fee=trading_fee, coins=coins)
