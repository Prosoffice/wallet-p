import decimal
import os
import random
import requests
from datetime import datetime


access_key = 'c5ea348edde57ad048840e0b00258e0b'



class CurrencyConvertor:
    # init dict to house the conversion rates
    rates = {}

    def __init__(self, url):
        data = requests.get(url).json()

        # Extracting only the rates from the json data
        self.rates = data["rates"]

    def convert(self, from_currency, to_currency, amount):

        # Get the EUR equivalent of the from_currency amount first
        initial_amount = amount
        if from_currency != 'EUR':
            amount = decimal.Decimal(initial_amount) / decimal.Decimal(self.rates[from_currency])

        # Multiply the from_currency (NOW IN EURO) by the EUR0 equivalent of the to_currency....round to 2dp
        converted_amount = round((amount * decimal.Decimal(self.rates[to_currency])), 2)
    
        return converted_amount



def convert_curr(from_currency, to_currency, amount):
    url = str.__add__('http://data.fixer.io/api/latest?access_key=', access_key)
    conversion_obj = CurrencyConvertor(url)
    try:
        converted = conversion_obj.convert(from_currency.upper(), to_currency.upper(), amount)
        return converted, True
    except Exception:
        return None, False


def generate_code(length):
    """Generate alphanunumeric code containing both lower case and upper case alphabets."""
    code = ''
    random.seed()
    for x in range(length):
        code += random.choice(
            [
                chr(random.choice(range(26)) + 0x41),
                chr(random.choice(range(26)) + 0x61),
                chr(random.choice(range(10)) + 0x30),
            ]
        )
    return code


def generate_wallet_id():
    
    code = generate_code(2)
    
    # Using timestamps to enforce wallet unique feature
    ts = int(datetime.now().timestamp())
    code = code + str(ts)
    return code



