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
    ticker_response = requests.get(ticker_url).json()
    info_response = requests.get(info_url).json()

    # Fetch USDT price
    usdt_price = 1.0
    for item in ticker_response:
        if item['symbol'] == 'USDTBUSD':
            usdt_price = float(item['price'])
            break

    # Create a dictionary of asset names for spot trading
    asset_names = {}
    for asset in info_response['symbols']:
        if asset['status'] != 'TRADING':
            continue
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
                    rate_1 = coins[base_asset][quote_asset_1] * (1 - trading_fee)
                    rate_2 = coins[quote_asset_1][quote_asset_2] * (1 - trading_fee)
                    rate_3 = coins[quote_asset_2][base_asset] * (1 - trading_fee)
                    if rate_1 * rate_2 * rate_3 > 1:
                        opportunity = {
                            'base_asset': base_asset,
                            'quote_asset_1': quote_asset_1,
                            'quote_asset_2': quote_asset_2,
                            'rate_1': rate_1,
                            'rate_2': rate_2,
                            'rate_3': rate_3,
                            'potential_profit': round(rate_1 * rate_2 * rate_3 - 1, 4),
                            'potential_profit_usdt': round((rate_1 * rate_2 * rate_3 - 1) * usdt_price, 4)
                        }
                        opportunities.append(opportunity)

    if not opportunities:
        # Fetch the 50 nearest opportunities and display
        sorted_coins = sorted(coins.keys())
        for i in range(len(sorted_coins)):
            for j in range(i + 1, len(sorted_coins)):
                if sorted_coins[j] not in coins[sorted_coins[i]]:
                    continue
                for k in range(j + 1, len(sorted_coins)):
                    if sorted_coins[k] not in coins[sorted_coins[j]]:
                        continue
                    if sorted_coins[i] in coins[sorted_coins[k]]:
                        rate_1 = coins[sorted_coins[i]][sorted_coins[j]] * (1 - trading_fee)
                        rate_2 = coins[sorted_coins[j]][sorted_coins[k]] * (1 - trading_fee)
                        rate_3 = coins[sorted_coins[k]][sorted_coins[i]] * (1 - trading_fee)
                        if rate_1 * rate_2 * rate_3 > 1:
                            opportunity = {
                                'base_asset': sorted_coins[i],
                                'quote_asset_1': sorted_coins[j],
                                'quote_asset_2': sorted_coins[k],
                                'rate_1': rate_1,
                                'rate_2': rate_2,
                                'rate_3': rate_3,
                                'potential_profit': round(rate_1 * rate_2 * rate_3 - 1, 4),
                                'potential_profit_usdt': round((rate_1 * rate_2 * rate_3 - 1) * usdt_price, 4)
                            }
                            opportunities.append(opportunity)
            if len(opportunities) > 50:
                break

    # Sort the opportunities by potential profit
    opportunities = sorted(opportunities, key=lambda x: x['potential_profit'], reverse=True)
    num_opportunities = len(opportunities)

    # Render the template with the opportunities
    return render_template('index.html', opportunities=opportunities,num_opportunities=num_opportunities)

if __name__ == '__main__':
    app.run(debug=True)
