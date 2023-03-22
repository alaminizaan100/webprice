from api import get_ticker_data, get_exchange_info
from algorithm import calculate_arbitrage_opportunities

def find_arbitrage_opportunities():
    # Get data from Binance API
    ticker_data = get_ticker_data()
    exchange_info = get_exchange_info()

    # Find triangular arbitrage opportunities
    opportunities = calculate_arbitrage_opportunities(ticker_data, exchange_info)

    # Calculate potential profit in USDT and deduct trading fee
    for opportunity in opportunities:
        opportunity['potential_profit'] = round(opportunity['potential_profit'] * (1 - 0.0015), 4)

    # Sort opportunities by potential profit
    opportunities = sorted(opportunities, key=lambda x: x['potential_profit'], reverse=True)
    num_opportunities = len(opportunities)

    return opportunities, num_opportunities
