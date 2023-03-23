from flask import Flask, render_template
from arbitrage import find_arbitrage_opportunities, get_ticker_data, get_exchange_info
from algorithm import calculate_arbitrage_opportunities
app = Flask(__name__)

@app.route('/')
def binance_data():
    ticker_data = get_ticker_data()
    exchange_info = get_exchange_info()
    opportunities = calculate_arbitrage_opportunities(ticker_data, exchange_info)
    num_opportunities = len(opportunities)

    return render_template('index.html', opportunities=opportunities, num_opportunities=num_opportunities)

if __name__ == '__main__':
    app.run(debug=True)
