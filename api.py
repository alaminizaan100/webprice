import requests

def get_ticker_data():
    # API endpoint for ticker prices
    ticker_url = 'https://api.binance.com/api/v3/ticker/price'

    # Make the API request
    ticker_response = requests.get(ticker_url).json()

    return ticker_response

def get_exchange_info():
    # API endpoint for exchange information
    info_url = 'https://api.binance.com/api/v3/exchangeInfo'

    # Make the API request
    info_response = requests.get(info_url).json()

    return info_response
