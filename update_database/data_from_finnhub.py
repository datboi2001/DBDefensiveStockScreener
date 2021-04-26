import finnhub as fh
import pandas as pd


def list_from_finnhub(exc: str) -> ({str}, str):
    """Gather a list of stocks from Finnhub based on exchange code.
    Validate exchange code from an excel file provided by Finnhub"""
    exc_file = pd.read_excel("exchange.xlsx")
    exc_list = exc_file['code']
    while exc not in exc_list.array:
        print("Invalid exchange. Try again.")
        exc = input("Please choose an exchange to update: ")
    api_client = fh.Client(api_key='btpvg6v48v6v5kvo1r10')
    raw_data = api_client.stock_symbols(exchange=exc.upper())
    all_stock = set()
    # Can fix this if you want to. Check out the stock symbols sections in Finnhub documentation
    stock_type = {'ADR', 'Common Stock', 'Unit', 'REIT', 'ETP', 'Ltd Part'}
    mic_code = {'XNAS', 'XNYS', 'HSTC', 'XSTC'}
    for i in raw_data:
        symbol_type = i['type']
        mic = i['mic']
        if symbol_type in stock_type and mic in mic_code:
            all_stock.add(i['symbol'])
    return all_stock, exc


def create_api_objects(api_key_file) -> [fh.Client]:
    """Get the API keys from the FinnhubAPIkey.txt
    and create a list of CLient objects using those keys.
    There are multiple Client objects since an
    API key can only perform 60 calls/minute."""
    api_objects = []
    for key in api_key_file:
        api_objects.append(fh.Client(api_key=key.rstrip()))
    return api_objects
