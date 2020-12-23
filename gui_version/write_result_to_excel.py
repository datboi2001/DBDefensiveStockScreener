from collections import defaultdict
from pathlib import Path
from pandas import DataFrame
import datetime as dt


def create_file_path(file_name: str, folder_path: Path) -> Path:
    c_time = dt.datetime.now()
    current_time = f"{c_time.hour}_{c_time.minute}_{c_time.second}"
    destination = folder_path / f"{file_name}_{current_time}.xlsx"
    return destination


def write_to_excel_and_save(location: Path, u_stocks_data: [(str)]) -> None:
    """Write all of the results on an excel file and place
    the file on the path the users provided."""
    excel_data = defaultdict(list)
    current = dt.datetime.now()
    today = f"{current.month}/{current.day}/{current.year}"
    for stocks in u_stocks_data:
        ticker, name, exchange, industry, company_website, market_cap, pe, pb,\
        ps, rg5y, current_price, high_price,updated_timestamp, roe = stocks
        excel_data['Ticker'].append(ticker)
        excel_data['Name'].append(name)
        excel_data['Exchange'].append(exchange)
        excel_data['Industry'].append(industry)
        excel_data["Company's website"].append(company_website)
        excel_data["Market Capitalization"].append(market_cap)
        excel_data['Current Price'].append(current_price)
        excel_data["High Price"].append(high_price)
        excel_data['PE'].append(pe)
        excel_data['PB'].append(pb)
        excel_data['PS'].append(ps)
        excel_data['RG5Y'].append(rg5y)
        excel_data['ROE'].append(roe)
        excel_data["Updated Timestamp"].append(updated_timestamp)
    result_df = DataFrame(excel_data)
    result_df.to_excel(location)