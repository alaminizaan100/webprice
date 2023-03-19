
from binance import AsyncClient, BinanceSocketManager
import asyncio
from flask import Flask, render_template

app = Flask(__name__)

# Define your Binance API keys
API_KEY = 'OtmdN18Tgx7VjnLyD4Ulc7ooNUaS0ezw38EZtTXvz0Eln4LxePIGCjOC95WG80OG'
API_SECRET = 'ShmYzH63927bieEp6SgHTDXv3hlEdkiePHMsSpdXpbviKNJbGpPSS6M3YSTACq4u'

# Create a Binance client and socket manager
client = AsyncClient(API_KEY, API_SECRET)
bm = BinanceSocketManager(client)

# Define the websocket endpoint to connect to
ws_endpoint = '!ticker@arr'

# Define the callback function for handling the websocket data
async def handle_socket_message(msg):
    # Send the websocket message to the index.html file using Flask-SocketIO
    await app.extensions['socketio'].emit('ticker', msg)

# Define the route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html')

# Define the function to start the websocket connection
async def start_websocket():
    # Create a websocket connection to the endpoint
    ws = bm.multiplex_socket([ws_endpoint])

    # Register the callback function to handle incoming data
    ws.register_callback(handle_socket_message)

    # Start the websocket connection
    await ws.__aenter__()

# Start the websocket connection when the Flask app starts
@app.before_first_request
async def start():
    await start_websocket()

if __name__ == '__main__':
    # Start the Flask app using Gunicorn
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    from gunicorn.workers.gthread import GThreadWorker
    from socketio import Server

    socketio = Server(async_mode='threading')
    app.extensions['socketio'] = socketio

    @app.before_first_request
    def start_background_thread():
        async def run():
            await start_websocket()
        asyncio.create_task(run())

    @socketio.on('connect')
    def connect():
        print('Client connected')

    @socketio.on('disconnect')
    def disconnect():
        print('Client disconnected')

    @socketio.on_error()
    def error_handler(e):
        print('Error:', e)

    @socketio.on('ticker')
    def handle_ticker(msg):
        socketio.emit('ticker', msg)

    app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'
    worker = GThreadWorker(app)
    worker.init_app(app)
    worker.run()
