from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def index():
    # Fetch the top 20 coins from CoinGecko API
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1&sparkline=false&price_change_percentage=1h%2C24h%2C7d%2C14d%2C30d%2C200d%2C1y'
    response = requests.get(url)
    coins = response.json()
    
    # Filter out only actively trading coins
    coins = [coin for coin in coins if coin['is_active']]
    
    # Sort coins based on market cap
    coins = sorted(coins, key=lambda x: x['market_cap'], reverse=True)
    
    # Fetch the price data for each coin on all exchanges
    all_prices = {}
    for coin in coins:
        symbol = coin['symbol']
        url = f'https://api.coingecko.com/api/v3/coins/{coin["id"]}/tickers'
        response = requests.get(url)
        tickers = response.json()['tickers']
        
        # Filter out non-USD trading pairs
        tickers = [t for t in tickers if t['target'] == 'USD']
        
        # Find the highest and lowest price exchanges for the coin
        highest_price = max(tickers, key=lambda x: x['last_trade']['p'])['market']['name']
        lowest_price = min(tickers, key=lambda x: x['last_trade']['p'])['market']['name']
        
        # Compute the price difference percentage
        highest_price_value = max(tickers, key=lambda x: x['last_trade']['p'])['last_trade']['p']
        lowest_price_value = min(tickers, key=lambda x: x['last_trade']['p'])['last_trade']['p']
        diff_percentage = round(((highest_price_value - lowest_price_value) / highest_price_value) * 100, 2)
        
        # Add the price data to the dictionary
        all_prices[symbol] = {
            'price': coin['current_price'],
            'highest_price': highest_price,
            'lowest_price': lowest_price,
            'diff_percentage': diff_percentage
        }
    
    return render_template('index.html', coins=all_prices)

if __name__ == '__main__':
    app.run(debug=True)
