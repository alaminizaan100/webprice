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
        if asset['status'] == 'BREAK':
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
                    potential_profit = rate_1 * rate_2 * rate_3 - 1
                    opportunity = {
                        'base_asset': base_asset,
                        'quote_asset_1': quote_asset_1,
                        'quote_asset_2': quote_asset_2,
                        'rate_1': rate_1,
                        'rate_2': rate_2,
                        'rate_3': rate_3,
                        'potential_profit': round(potential_profit, 4),
                        'potential_profit_usdt': round(potential_profit * usdt_price, 4)
                    }
                    opportunities.append(opportunity)

    # Sort opportunities by potential profit
    opportunities = sorted(opportunities, key=lambda x: x['potential_profit'], reverse=True)

    # Add color codes based on profitability
    for opportunity in opportunities:
        if opportunity['potential_profit'] > 0:
            opportunity['color'] = 'green'
        else:
            opportunity['color'] = 'red'

    num_opportunities = len(opportunities)

    # Print the opportunities and their profitability
    print(f"Found {num_opportunities} triangular arbitrage opportunities:\n")
    for opportunity in opportunities:
        print(f"{opportunity['base_asset']} -> {opportunity['quote_asset_1']} -> {opportunity['quote_asset_2']} -> {opportunity['base_asset']}:")
        print(f"Rate 1: {opportunity['rate_1']:.8f}")
        print(f"Rate 2: {opportunity['rate_2']:.8f}")
        print(f"Rate 3: {opportunity['rate_3']:.8f}")
        print(f"Potential Profit: {opportunity['potential_profit_usdt']:.8f} USDT")
        print(f"Color: {opportunity['color']}\n")

    # Return the opportunities to the web page
    return render_template('index.html', opportunities=opportunities, num_opportunities=num_opportunities)
if __name__ == '__main__':
    app.run(debug=True)
