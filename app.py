from flask import Flask, render_template
import requests

app = Flask(__name__)

def get_coins():
    # List of active trading coins
    url = "https://min-api.cryptocompare.com/data/top/mktcapfull?limit=100&tsym=USD"
    coins = requests.get(url).json()['Data']

    # List of exchanges to fetch coin prices from
    exchanges = ['Binance', 'Kucoin', 'Bitget', 'MEXC Global', 'Bitstamp', 'Bitfinex', 'Gate.io', 'Bithumb', 'Huobi', 'WhiteBIT', 'EXMO']

    result = []
    for coin in coins:
        # Add a new 'prices' key to each coin dictionary
        coin_dict = {}
        coin_dict['prices'] = {}
        for exchange in exchanges:
            # Fetch coin price from the exchange
            url = f"https://min-api.cryptocompare.com/data/price?fsym={coin['CoinInfo']['Name']}&tsyms={exchange}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # Add coin price to the 'prices' dictionary for the exchange
                if data.get(exchange):
                    coin_dict['prices'][exchange] = data[exchange]

        # Remove coins with no active trading markets
        coin_dict['is_active'] = len(coin_dict['prices']) > 0
        if coin_dict['is_active']:
            # Add other keys to the coin dictionary
            coin_dict['id'] = coin['CoinInfo']['Id']
            coin_dict['name'] = coin['CoinInfo']['FullName']
            coin_dict['symbol'] = coin['CoinInfo']['Name']
            result.append(coin_dict)

    return result

@app.route('/')
def index():
    coins = get_coins()

    for coin in coins:
        # Find the exchange with the lowest and highest coin price
        prices = coin['prices']
        low_exchange = min(prices, key=lambda k: prices[k])
        high_exchange = max(prices, key=lambda k: prices[k])

        # Calculate the price difference in percentage
        low_price = prices[low_exchange]
        high_price = prices[high_exchange]
        if low_price == 0:
            percentage_diff = float('inf')
        else:
            percentage_diff = (high_price - low_price) / low_price * 100

        # Add the lowest and highest exchange name and percentage difference to the coin dictionary
        coin['low_exchange'] = low_exchange
        coin['high_exchange'] = high_exchange
        coin['percentage_diff'] = round(percentage_diff, 2)

    # Sort coins by percentage difference
    coins = sorted(coins, key=lambda k: k['percentage_diff'], reverse=True)

    return render_template('index.html', coins=coins)


if __name__ == '__main__':
    app.run(debug=True)
