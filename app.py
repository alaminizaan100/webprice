from flask import Flask, render_template
import ccxt.async as ccxt
import asyncio

app = Flask(__name__)

async def scan_arbitrage(exchanges):
    result = []

    # Connect to each exchange asynchronously
    for exchange in exchanges:
        await exchange.load_markets()

    # Check for arbitrage opportunities
    for i in range(len(exchanges)):
        for j in range(i+1, len(exchanges)):
            exchange1 = exchanges[i]
            exchange2 = exchanges[j]

            # Get all symbols with both exchanges
            symbols = set(exchange1.symbols) & set(exchange2.symbols)

            # Check for arbitrage opportunities in each symbol
            for symbol in symbols:
                try:
                    ticker1 = await exchange1.fetch_ticker(symbol)
                    ticker2 = await exchange2.fetch_ticker(symbol)

                    # Calculate potential profit percentage
                    bid1 = ticker1['bid']
                    ask2 = ticker2['ask']
                    profit_percent = (ask2 - bid1) / bid1 * 100

                    # Add arbitrage opportunity to results if profit percentage is positive
                    if profit_percent > 0:
                        result.append({
                            'symbol': symbol,
                            'exchange1': exchange1.id,
                            'exchange2': exchange2.id,
                            'bid1': bid1,
                            'ask2': ask2,
                            'profit_percent': profit_percent
                        })
                except ccxt.errors.ExchangeError as e:
                    print(f"Error fetching ticker for {symbol} on {exchange1.id} and {exchange2.id}: {e}")

    return result

@app.route('/')
def index():
    # Create a list of exchange instances
    exchanges = [ccxt.binance(), ccxt.bitfinex(), ccxt.bittrex(), ccxt.coinbasepro(), ccxt.huobipro(), ccxt.kraken(), ccxt.okex(), ccxt.poloniex(), ccxt.upbit(), ccxt.zb()]

    # Scan for arbitrage opportunities
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(scan_arbitrage(exchanges))

    # Render the template with the results
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
