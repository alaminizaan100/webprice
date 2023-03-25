from flask import Flask, render_template
import ccxt

app = Flask(__name__)

@app.route('/')
def index():
    # Exchange objects for Binance and KuCoin
    binance = ccxt.binance()
    kucoin = ccxt.kucoin({
        'enableRateLimit': True,
        'apiKey': 'YOUR_API_KEY',
        'secret': 'YOUR_SECRET_KEY',
    })
    
    # Get all the markets available on both exchanges
    binance_markets = binance.load_markets()
    kucoin_markets = kucoin.load_markets()
    
    # Find the common markets between Binance and KuCoin
    common_markets = set(binance_markets.keys()) & set(kucoin_markets.keys())
    
    # Create a list of dictionaries for all the common markets with arbitrage opportunity
    arbitrage_opportunities = []
    for market in common_markets:
        # Get the ticker information for the market on both exchanges
        binance_ticker = binance.fetch_ticker(market)
        kucoin_ticker = kucoin.fetch_ticker(market)
        
        # Calculate the arbitrage opportunity
        amount_bought = (100 / binance_ticker['ask']) * (1 - binance.fees['trading']['taker'])
        amount_sold = amount_bought * kucoin_ticker['bid'] * (1 - kucoin.fees['trading']['taker']) - kucoin.fees['withdraw'][kucoin_ticker['symbol'].split('/')[0]]
        arbitrage = amount_sold - 100
        
        # If the arbitrage opportunity is positive, add it to the list of opportunities
        if arbitrage > 0:
            binance_withdraw_fee = binance.fees['withdraw'][binance_ticker['symbol'].split('/')[0]]
            kucoin_withdraw_fee = kucoin.fees['withdraw'][kucoin_ticker['symbol'].split('/')[0]]
            arbitrage_opportunities.append({
                'market': market,
                'arbitrage': round(arbitrage, 2),
                'binance_withdraw_fee': binance_withdraw_fee,
                'kucoin_withdraw_fee': kucoin_withdraw_fee,
            })
    
    # Render the HTML template with the list of opportunities
    return render_template('index.html', opportunities=arbitrage_opportunities)

if __name__ == '__main__':
    app.run(debug=True)
