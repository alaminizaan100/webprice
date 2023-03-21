from flask import Flask, render_template
from flask_socketio import SocketIO
import ccxt
import eventlet

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Initialize Binance exchange
binance = ccxt.binance()

# Define WebSocket event handler
@socketio.on('connect')
def handle_connect():
    # Start WebSocket connection to Binance
    symbol = 'BTC/USDT'  # Set default symbol to BTC/USDT
    binance.load_markets()
    binance_symbol = binance.symbol(symbol)
    binance.websocket_subscribe(binance_symbol, 'ticker', callback)

def callback(ticker):
    # Send ticker data to the WebSocket client
    socketio.emit('ticker', {
        'symbol': ticker['symbol'],
        'price': ticker['last'],
    })

# Define Flask route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Run Flask app with SocketIO
    eventlet.monkey_patch()
    socketio.run(app)
