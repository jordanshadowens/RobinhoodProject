import robin_stocks.robinhood as r
import pyotp
import asyncio
import pandas as pd


def start_script():
    loop = asyncio.get_event_loop()
    totp = pyotp.TOTP("My2factorAppHere").now()
    r.login('EMAIL_HERE', 'PASSWORD', mfa_code=totp)
    historic_prices = {
        'price': []
    }
    historic_ema = {
        'ema': []
    }

    # positions = r.crypto.get_crypto_positions(info=None)

    def sma():
        price_frame = pd.DataFrame(historic_prices)
        x = price_frame['price'].tail(12)
        list = x.tolist()
        count = 0
        for price in list:
            count = price + count
        sma = count / 12
        print(f"SMA is {sma}")
        historic_ema['ema'].append(sma)
        loop.call_soon(calculateEma)

    def calculateEma():
        price_frame = pd.DataFrame(historic_prices)
        ema_frame = pd.DataFrame(historic_ema)
        k = .1538
        last_price = price_frame['price'].tail(1).tolist()
        last_ema = ema_frame['ema'].tail(1).tolist()
        a = last_price[0] * k
        b = last_ema[0] * (1 - k)
        ema = a + b
        print(f"First EMA is {ema}")
        historic_ema['ema'].append(ema)
        loop.call_later(900, calculateEma)

    def gatherData():
        crypto = r.crypto.get_crypto_quote('BTC', info=None)
        price = float(crypto['mark_price'])
        historic_prices['price'].append(price)
        print(f"Current historical price array {historic_prices['price']}")
        loop.call_later(900, gatherData)

    def buybitcoin():
        ema_frame = pd.DataFrame(historic_ema)
        crypto = r.crypto.get_crypto_quote('BTC', info=None)
        price = float(crypto['mark_price'])
        last_ema = ema_frame['ema'].tail(1).tolist()
        print(f"Current EMA is {last_ema[0]}")
        if price > last_ema[0]:
            profile = r.profiles.load_account_profile(info=None)
            cash = float(profile['portfolio_cash'])
            cash = "{:.2f}".format(cash)
            print(cash)
            info = r.orders.order_crypto('BTC', 'buy', float(cash), amountIn='price', limitPrice=None, timeInForce='gtc', jsonify=True)
            print(info)
        else:
            sellbitcoin()
        loop.call_later(900, buybitcoin)

    def sellbitcoin():
        positions = r.crypto.get_crypto_positions(info=None)
        arr = positions[0]
        cost_bases = arr['cost_bases']
        details = cost_bases[0]
        quantity = float(details['direct_quantity'])
        print(quantity)
        info = r.orders.order_crypto('BTC', 'sell', quantity, amountIn='quantity', limitPrice=None, timeInForce='gtc',
                                     jsonify=True)
        print(info)

    loop.call_soon(gatherData)
    loop.call_later(10800, sma)
    loop.call_later(11700, buybitcoin)
    loop.run_forever()


start_script()
