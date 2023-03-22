def calculate_arbitrage_opportunities(ticker_data, exchange_info):
    opportunities = []
    for base_asset in coins:
        for quote_asset_1 in coins[base_asset]:
            if quote_asset_1 not in coins:
                continue
            for quote_asset_2 in coins[quote_asset_1]:
                if quote_asset_2 not in coins:
                    continue
                if base_asset in coins[quote_asset_2]:
                    rate_1 = coins[base_asset][quote_asset_1]
                    rate_2 = coins[quote_asset_1][quote_asset_2]
                    rate_3 = coins[quote_asset_2][base_asset]
                    if rate_1 * rate_2 * rate_3 > 1:
                        opportunity = {
                            'base_asset': base_asset,
                            'quote_asset_1': quote_asset_1,
                            'quote_asset_2': quote_asset_2,
                            'rate_1': rate_1,
                            'rate_2': rate_2,
                            'rate_3': rate_3,
                            'potential_profit': round(rate_1 * rate_2 * rate_3 - 1, 4)
                        }
                        opportunities.append(opportunity)

    return opportunities
