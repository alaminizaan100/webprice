from flask import Flask, render_template
import requests
app = Flask(__name__)
@app.route('/')
def index():
    # Get current trading prices for Bitcoin, Ethereum, and Litecoin from CoinGecko API
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,litecoin&vs_currencies=usd&include_24hr_change=true'
    data = requests.get(url).json()
    # Get top 10 crypto exchanges from CoinGecko API
    url = 'https://api.coingecko.com/api/v3/exchanges?per_page=10'
    exchanges = requests.get(url).json()
    # Create a dictionary to store prices and arbitrage for each coin
    prices = {}
    arbitrage = {}
    # Loop through the top 10 exchanges and get trading prices for each coin
    for exchange in exchanges:
        exchange_name = exchange['name']
        exchange_id = exchange['id']
        exchange_url = f'https://api.coingecko.com/api/v3/exchanges/{exchange_id}?tickers=true&per_page=100&page=1'
        exchange_data = requests.get(exchange_url).json()
        tickers = exchange_data['tickers']
        for ticker in tickers:
            if ticker['target'] == 'USD':
                coin = ticker['base']
                price = ticker['last']
                change = ticker['converted_last']['usd_24h_change']
                if coin not in prices:
                    prices[coin] = {}
                    arbitrage[coin] = {}
                prices[coin][exchange_name] = price
                arbitrage[coin][exchange_name] = None
    # Calculate arbitrage for each coin
    for coin in prices:
        for exchange1 in prices[coin]:
            for exchange2 in prices[coin]:
                if exchange1 != exchange2:
                    arb = prices[coin][exchange2] - prices[coin][exchange1]
                    if arbitrage[coin][exchange1] is None or arb > arbitrage[coin][exchange1]:
                        arbitrage[coin][exchange1] = arb
    # Render template with prices and arbitrage for each coin
    return render_template('index.html', prices=prices, arbitrage=arbitrage)
if __name__ == '__main__':
    app.run(debug=True)
