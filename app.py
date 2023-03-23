from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def binance_data():
    ticker_response = requests.get('https://api.binance.com/api/v3/ticker/price').json()
    info_response = requests.get('https://api.binance.com/api/v3/exchangeInfo').json()
    trading_fee = 0.001
    usdt_price = 1.0
    for item in ticker_response:
        if item['symbol'] == 'USDTBUSD':
            usdt_price = float(item['price'])
            break
    asset_names = {}
    for asset in info_response['symbols']:
        if asset['status'] != 'TRADING':
            continue
        asset_names[asset['symbol']] = {
            'base': asset['baseAsset'],
            'quote': asset['quoteAsset']
        }
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

    # filter out opportunities with potential profit less than or equal to 0
    opportunities = [o for o in opportunities if o['potential_profit'] > 0]
    
    # sort the remaining opportunities by potential profit in descending order
    opportunities = sorted(opportunities, key=lambda x: x['potential_profit'], reverse=True)
    
    # if there are no opportunities left, return a message
    if len(opportunities) == 0:
        return "No profitable opportunities found."
    
    # get the first opportunity as the nearest one
    nearest_opportunity = opportunities[0]
    
    return render_template('index.html', opportunities=opportunities, num_opportunities=len(opportunities), nearest_opportunity=nearest_opportunity)

if __name__ == '__main__':
    app.run(debug=True)
