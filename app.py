from flask import Flask, Response
import websocket
import json

app = Flask(__name__)

def on_message(ws, message):
    data = json.loads(message)
    if data['e'] == 'error':
        print(f"Error: {data['m']}")
        return
    if data['e'] == '24hrTicker':
        symbol = data['s']
        price = data['c']
        response = f"{symbol}: {price}"
        return Response(response=response, mimetype='text/plain')

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")
    ws.send('{"method": "SUBSCRIBE","params": ["!ticker@arr"],"id": 1}')

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/binance')
def binance():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/!ticker@arr", on_message = on_message, on_error = on_error, on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

if __name__ == '__main__':
    app.run()
