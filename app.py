import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    if data['e'] == 'error':
        print(f"Error: {data['m']}")
        return
    if data['e'] == '24hrTicker':
        symbol = data['s']
        price = data['c']
        print(f"{symbol}: {price}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")
    ws.send('{"method": "SUBSCRIBE","params": ["!ticker@arr"],"id": 1}')

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/!ticker@arr", on_message = on_message, on_error = on_error, on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
