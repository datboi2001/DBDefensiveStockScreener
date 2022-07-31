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
    result_df = DataFrame(u_stocks_data, columns=columns)
    result_df.to_excel(location)
