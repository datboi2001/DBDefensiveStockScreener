import logging
import time
import finnhub as fh
import psycopg2
from psycopg2 import extensions
from stock import Stock
from queue import SimpleQueue, Empty
from typing import Tuple
from random import choice
from credentials import username, host, port, dbname, passcode
InsertQueue = SimpleQueue()
UpdateQueue = SimpleQueue()

logging.basicConfig(format='%(asctime)s  %(message)s',
                    datefmt='%H:%M:%S', level=logging.INFO)


def create_global_queue(insert_set: {str}, update_set: {str}) -> None:
    """Create queue for the threading functions"""
    if insert_set:
        for i in insert_set:
            InsertQueue.put(i)
    if update_set:
        for k in update_set:
            UpdateQueue.put(k)


def _create_table_if_not_exist(table_name: str, cursor: extensions.cursor) -> None:
    """Create a table based on the table_name."""
    command = f"""create table {table_name}
(ticker varchar(50) not null, name varchar(255), exchange varchar(255), industry varchar(255),
company_website varchar(255), market_cap bigint, pe double precision, pb double precision, ps double precision,
rg5y double precision, roe double precision, current_price double precision, high_price double precision,
updated_timestamp timestamp);

create unique index {table_name}_ticker_uindex on {table_name} (ticker);

alter table {table_name} add constraint {table_name}_pk primary key (ticker);"""
    cursor.execute(command)


def check_for_existence(table_name: str, cursor: extensions.cursor) -> None:
    """Check if a table with table_name exists in the database.
    Call a helper function to create a new table if
    the database doesn't have """
    command = f"SELECT to_regclass('public.{table_name}')"
    cursor.execute(command)
    result = cursor.fetchall()[0][0]
    if result is None:
        _create_table_if_not_exist(table_name, cursor)
        print(f"Created a new table, code is {table_name}.")


def create_connection(amount: int) -> [extensions.connection, Tuple[extensions.cursor]] or psycopg2.Error:
    """Create connection and cursor to PostgreSQL database"""
    # noinspection PyInterpreter
    try:
        conn = psycopg2.connect(dbname=dbname, user=username,
                                password=passcode, host=host,
                                port=port)
    except psycopg2.Error as error:
        return error
    else:
        cur = tuple(conn.cursor() for _ in range(amount))
        conn.autocommit = True
        return [conn, cur]


def _fixed_delay(call, **kwargs) -> dict:
    """Make API calls and pause the program
    when API limits has been reached."""
    start = time.perf_counter() + 1
    try:
        ret = call(**kwargs)
    except fh.FinnhubAPIException:
        time.sleep(60)
        ret = call(**kwargs)
    diff = start - time.perf_counter()
    if diff > 0:
        time.sleep(diff)
    return ret


def _insert_metrics(stock_object: Stock, fin_metrics: dict, quote: dict, stock_info: dict) -> None:
    """Insert data gathered from API into the Stock object
        if they exist otherwise do nothing."""
    if stock_info != {}:
        o_name = stock_info['name']
        o_exchange = stock_info['exchange']
        o_industry = stock_info['finnhubIndustry']
        o_web_url = stock_info['weburl']
        stock_object.modify_attributes(name=o_name, exchange=o_exchange, industry=o_industry, weburl=o_web_url)
    if fin_metrics != {} and fin_metrics['metric'] != {}:
        metric = fin_metrics['metric']
        o_h_price = metric['52WeekHigh']
        o_pb = metric['pbAnnual']
        o_rg5y = metric['revenueGrowth5Y']
        o_ps = metric['psTTM']
        if metric['marketCapitalization'] is not None:
            o_market_cap = metric['marketCapitalization'] * 10 ** 6
            stock_object.modify_attributes(market_cap=o_market_cap)
        o_pe = metric['peExclExtraTTM']
        o_roe = metric['roeTTM']
        stock_object.modify_attributes(h_price=o_h_price, pe=o_pe,
                                       pb=o_pb, rg5y=o_rg5y, ps=o_ps, roe=o_roe)
    if quote != {}:
        o_c_price = quote['c']
        stock_object.modify_attributes(c_price=o_c_price)


def retrieve_db_stock_list(cursor: extensions.cursor, exc: str) -> {str} or set:
    """Gather all of the stock ticker from database"""
    cursor.execute(f"SELECT ticker from {exc}")
    db_stocks = cursor.fetchall()
    if db_stocks:
        return {stock[0] for stock in db_stocks}
    return set()


def find_insert_delete_update(fh_stock: {str}, db_stock: {str}) -> ({str}, {str}, {str}):
    """Find stocks to inserts, update, and delete using operations with sets."""
    insert_stocks = fh_stock - db_stock
    delete_stocks = db_stock - fh_stock
    update_stocks = fh_stock & db_stock
    return delete_stocks, insert_stocks, update_stocks


def _execute_command(cursor: extensions.cursor, exc: str, stock: Stock, insert=False, update=False, remove=False):
    """Execute a command to the database whether it's updating, deleting or inserting
    a new stock into the database."""
    value_dict = stock.return_all_attributes()
    command = ''
    if insert:
        command = f"""INSERT INTO {exc}(ticker, name, exchange, industry, company_website, market_cap, pe,
        pb, ps, rg5y, current_price, high_price, updated_timestamp, roe) VALUES(%(symbol)s, %(name)s, %(exchange)s,
        %(industry)s, %(weburl)s, %(market_cap)s, %(pe)s, %(pb)s, %(rg5y)s, %(ps)s, %(c_price)s, %(h_price)s,
        %(timestamp)s, %(roe)s)"""
    elif update:
        command = f"""UPDATE {exc} SET market_cap = %(market_cap)s, pe = %(pe)s,
         pb = %(pb)s, rg5y = %(rg5y)s, current_price = %(c_price)s, high_price = %(h_price)s, ps = %(ps)s,
        updated_timestamp = %(timestamp)s, roe = %(roe)s WHERE ticker = %(symbol)s;"""
    elif remove:
        command = f"""DELETE FROM {exc} WHERE ticker = %(symbol)s;"""
    cursor.execute(command, value_dict)

#For testing since it's impossible to debug a program with multiple threads
#---------------------------------------------------------------------------------------------------------------------

def insert_stocks_into_db_test(cursor, api_objects, exc) -> None:
    """Make API calls to finnhub and insert the stock in InsertQueue into
    a SQL database. Cursor will handle the job of inserting and committing changes
    to the database."""
    # cursor, api_object, exc = cursor_api
    while True:
        try:
            stock = InsertQueue.get(block=False)
        except Empty:
            break
        api_object = choice(api_objects)
        info = _fixed_delay(api_object.company_profile2, symbol=stock)
        metrics = _fixed_delay(api_object.company_basic_financials, symbol=stock, metric="all")
        price_info = {'c': 0}
        if exc == 'US':
            price_info = _fixed_delay(api_object.quote, symbol=stock)
        new_stock = Stock(symbol=stock)
        _insert_metrics(new_stock, metrics, price_info, info)
        _execute_command(cursor, exc, new_stock, insert=True)
        logging.info(f"Inserted {stock} into database.")


def update_stocks_into_db_test(cursor, api_objects, exc) -> None:
    """Make API calls to Finnhub and update the stocks in UpdateQueue. Cursor
    will handle the job of updating and committing changes to the databases."""
    # cursor, api_object, exc = cursor_api
    while True:
        try:
            stock = UpdateQueue.get(block=False)
        except Empty:
            break
        api_object = choice(api_objects)
        metrics = _fixed_delay(api_object.company_basic_financials, symbol=stock, metric="all")
        price_info = {'c': 0}
        if exc == 'US':
            price_info = _fixed_delay(api_object.quote, symbol=stock)
        new_stock = Stock(symbol=stock)
        _insert_metrics(new_stock, metrics, price_info, {})
        _execute_command(cursor, exc, new_stock, update=True)
        logging.info(f"Updated {stock}.")



# Threading
#----------------------------------------------------------------------------------------------------------------------

def insert_stocks_into_db(cursor_api: [extensions.cursor, fh.Client, str]) -> None:
    """Make API calls to finnhub and insert the stock in InsertQueue into
    a SQL database. Cursor will handle the job of inserting and committing changes
    to the database."""
    cursor, api_object, exc = cursor_api
    while True:
        try:
            stock = InsertQueue.get(block=False)
        except Empty:
            break
        info = _fixed_delay(api_object.company_profile2, symbol=stock)
        metrics = _fixed_delay(api_object.company_basic_financials, symbol=stock, metric="all")
        price_info = {'c': 0}
        if exc == 'US':
            price_info = _fixed_delay(api_object.quote, symbol=stock)
        new_stock = Stock(symbol=stock)
        _insert_metrics(new_stock, metrics, price_info, info)
        _execute_command(cursor, exc, new_stock, insert=True)
        logging.info(f"Inserted {stock} into database.")


def update_stocks_into_db(cursor_api: [extensions.cursor, fh.Client, str]) -> None:
    """Make API calls to Finnhub and update the stocks in UpdateQueue. Cursor
    will handle the job of updating and committing changes to the databases."""
    cursor, api_object, exc = cursor_api
    while True:
        try:
            stock = UpdateQueue.get(block=False)
        except Empty:
            break
        metrics = _fixed_delay(api_object.company_basic_financials, symbol=stock, metric="all")
        price_info = {'c': 0}
        if exc == 'US':
            price_info = _fixed_delay(api_object.quote, symbol=stock)
        new_stock = Stock(symbol=stock)
        _insert_metrics(new_stock, metrics, price_info, {})
        _execute_command(cursor, exc, new_stock, update=True)
        logging.info(f"Updated {stock}.")
#----------------------------------------------------------------------------------------------------------------------

def delete_stocks_from_db(cursor: extensions.cursor, delete_stocks: {str}, exc_name: str) -> None:
    """Make API calls to Finnhub and delete any stocks in DeleteQueue from the database.
    Cursor will handle the job of deleting and comiiting changes to the database."""
    for stock in delete_stocks:
        delete_stock = Stock(symbol=stock)
        _execute_command(cursor, exc_name, delete_stock, remove=True)
        logging.info(f"Delete {stock} from database.")
    logging.info(f"Deleting a total of {len(delete_stocks)}")


def close_connection(conn: extensions.connection, cur: Tuple[extensions.cursor]) -> None:
    """Close all of the connections after the task is done"""
    conn.close()
    for c in cur:
        c.close()
