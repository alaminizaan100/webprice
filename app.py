from flask import Flask, jsonify, render_template
import websocket
import json
import threading

app = Flask(__name__)

@app.route('/binance')
def binance():
    data_dict = {}

    def on_message(ws, message):
        data = json.loads(message)
        if data['e'] == 'error':
            print(f"Error: {data['m']}")
            return
        if data['e'] == '24hrTicker':
            symbol = data['s']
            price = data['c']
            # Add the data to a dictionary
            data_dict[symbol] = price

    def on_error(ws, error):
        print(f"Error: {error}")

    def on_close(ws):
        print("Connection closed")

    def on_open(ws):
        print("Connection opened")
        ws.send('{"method": "SUBSCRIBE","params": ["!ticker@arr"],"id": 1}')

    def run_ws():
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/!ticker@arr", on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever()

    # Start the WebSocket connection in a new thread
    ws_thread = threading.Thread(target=run_ws)
    ws_thread.start()

    # Return the data as a JSON response
    return render_template('index.html', data_dict=data_dict)

if __name__ == '__main__':
    app.run(debug=True)
