from binance import AsyncClient, BinanceSocketManager
from flask import Flask, render_template
import asyncio

app = Flask(__name__)

# Set up Binance API keys
api_key = "your_api_key"
api_secret = "your_api_secret"

# Set up the WebSocket manager
client = AsyncClient(api_key=api_key, api_secret=api_secret)
bsm = BinanceSocketManager(client)

# Define a dictionary to store the latest data for each coin pair
latest_data = {}

# Define the route to display the coin data
@app.route('/')
def index():
    return render_template('index.html', latest_data=latest_data)

# Define the WebSocket stream handler function
async def process_message(msg):
    if msg['e'] == 'error':
        print(f"Error: {msg['m']}")
    else:
        # Extract the coin symbol, price, and other relevant data from the message
        symbol = msg['s']
        price = msg['c']
        info = msg['i']

        # Update the latest data dictionary with the new data for this coin pair
        latest_data[symbol] = {'price': price, 'info': info}

        # Update the HTML file with the new data
        # You will need to customize this part to fit your HTML file
        update_html(latest_data)

# Subscribe to the WebSocket stream for all coins and pairs on the exchange
async def subscribe_to_all():
    exchange_info = await client.get_exchange_info()
    symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
    streams = [f'{symbol.lower()}@ticker' for symbol in symbols]
    bm = bsm.multiplex_socket(streams, process_message)
    await bsm.start()

# Define a function to update the HTML file with the latest data
def update_html(latest_data):
    # Loop through the latest data dictionary and generate the HTML for each coin pair
    html = ''
    for symbol, data in latest_data.items():
        html += f'<div><span>{symbol}</span><span>{data["price"]}</span><span>{data["info"]}</span></div>'
    # Send the HTML to the client using Flask's built-in template rendering
    return render_template('index.html', latest_data=latest_data, html=html)

# Start the Flask app and subscribe to the WebSocket stream
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(subscribe_to_all())
    app.run()
