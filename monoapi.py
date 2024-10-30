import requests

def cr():
    url = 'https://api.monobank.ua/bank/currency'
    response = requests.get(url)
    data = response.json()

    currencies = dict(USD=840, EUR=978)

    result = []
    for item in data:
        if item.get('currencyCodeA') in currencies.values() and item.get('currencyCodeB') == 980:
            currency_name = list(currencies.keys())[list(currencies.values()).index(item['currencyCodeA'])]
            rate_buy = item.get('rateBuy')
            rate_sell = item.get('rateSell')
            result.append(f"{currency_name}: Покупка - 💵{rate_buy}, Продажа - 💸{rate_sell}")

    return "\n".join(result)