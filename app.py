from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def binance_data():
    # API endpoint for ticker prices
    ticker_url = 'https://api.binance.com/api/v3/ticker/price'
    # API endpoint for exchange information
    info_url = 'https://api.binance.com/api/v3/exchangeInfo'

    # Make the API requests
    ticker_response = requests.get(ticker_url).json()
    info_response = requests.get(info_url).json()

    # Create a dictionary of asset names
    asset_names = {}
    for asset in info_response['symbols']:
        asset_names[asset['symbol']] = {
            'base': asset['baseAsset'],
            'quote': asset['quoteAsset']
        }

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
                    rate_1 = coins[base_asset][quote_asset_1] * 0.999 # Apply 0.1% trading fee
                    rate_2 = coins[quote_asset_1][quote_asset_2] * 0.999 # Apply 0.1% trading fee
                    rate_3 = coins[quote_asset_2][base_asset] * 0.999 # Apply 0.1% trading fee
                    potential_profit = ((100 / rate_1) * rate_2 * rate_3 - 100) * 100 / 100 # Calculate potential profit with initial investment of 100 USD and convert to percentage
                    if potential_profit > 0:
                        opportunity = {
                            'base_asset': base_asset,
                            'quote_asset_1': quote_asset_1,
                            'quote_asset_2': quote_asset_2,
                            'rate_1': rate_1,
                            'rate_2': rate_2,
                            'rate_3': rate_3,
                            'potential_profit': round(potential_profit, 4)
                        }
                        opportunities.append(opportunity)

    opportunities = sorted(opportunities, key=lambda x: x['potential_profit'], reverse=True)
    num_opportunities = len(opportunities)

    for opportunity in opportunities:
        base_asset = opportunity['base_asset']
        quote_asset_1 = opportunity['quote_asset_1']
        quote_asset_2 = opportunity['quote_asset_2']
        profit = opportunity['potential_profit']
        buy_sell = base_asset + "/" + quote_asset_1 + "/" + quote_asset_2
        sell_buy = quote_asset_2 + "/" + quote_asset_1 + "/" + base_asset
        opportunity['buy_sell'] = buy_sell
        opportunity['sell_buy'] = sell_buy

    return render_template('index.html', opportunities=opportunities, num_opportunities=num_opportunities)


if __name__ == '__main__':
    app.run(debug=True)
