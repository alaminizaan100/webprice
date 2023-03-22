from flask import Flask, render_template
from arbitrage import find_arbitrage_opportunities

app = Flask(__name__)

@app.route('/')
def binance_data():
    opportunities, num_opportunities = find_arbitrage_opportunities()

    return render_template('index.html', opportunities=opportunities, num_opportunities=num_opportunities)

if __name__ == '__main__':
    app.run(debug=True)
