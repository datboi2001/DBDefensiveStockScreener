from collections import defaultdict
from pathlib import Path
from pandas import DataFrame
import datetime as dt


def create_file_path(file_name: str, folder_path: Path) -> Path:
    """Create a file path to save the result"""
    c_time = dt.datetime.now()
    current_time = f"{c_time.hour}_{c_time.minute}_{c_time.second}"
    destination = folder_path / f"{file_name}_{current_time}.xlsx"
    return destination


def write_to_excel_and_save(location: Path, u_stocks_data: [(str,)]) -> None:
    """Write all of the results on an excel file and place
    the file on the path the users provided."""
    excel_data = defaultdict(list)
    current = dt.datetime.now()
    today = f"{current.month}/{current.day}/{current.year}"
    columns = ['Ticker', 'Name', 'Exchange', 'Industry', "Company's website", "Market Capitalization",
               'PE', 'PB', 'PS', 'RG5Y', 'ROE', 'Current Price', 'High Price', 'Update Timestamp']
    for stocks in u_stocks_data:
        for col, val in zip(columns, stocks):
            excel_data[col].append(val)
        # ticker, name, exchange, industry, company_website, market_cap, pe, pb,\
        # ps, rg5y, current_price, high_price, updated_timestamp, roe = stocks
        # excel_data[].append(ticker)
        # excel_data[].append(name)
        # excel_data[].append(exchange)
        # excel_data[].append(industry)
        # excel_data[].append(company_website)
        # excel_data[].append(market_cap)
        # excel_data[].append(current_price)
        # excel_data[].append(high_price)
        # excel_data[].append(pe)
        # excel_data[].append(pb)
        # excel_data[].append(ps)
        # excel_data[].append(rg5y)
        # excel_data[].append(roe)
        # excel_data[].append(updated_timestamp)
    result_df = DataFrame(excel_data)
    result_df.to_excel(location)
