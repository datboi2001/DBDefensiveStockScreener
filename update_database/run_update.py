from codetiming import Timer
import update_stock_database as usd
import data_from_finnhub as get_fh
from concurrent.futures import ThreadPoolExecutor


def run_program() -> None:
    """Main program"""
    timer = Timer()
    timer.start()
    api_objects = get_fh.create_api_objects(open("FinnhubAPIkey.txt"))
    if not api_objects:
        return
    components = usd.create_connection(len(api_objects))
    if type(components) is list:
        connection, cursor = components
    else:
        print(components)
        return
    for exchange in open("exchange.txt"):
        if not exchange.startswith("#") and exchange.rstrip('\n') != '':
            fh_stock, exc = get_fh.list_from_finnhub(exchange.rstrip('\n'))
            print(f"Updating the {exc} exchange.")
            usd.check_for_existence(exc, cursor[0])
            db_stock_list = usd.retrieve_db_stock_list(cursor[0], exc)
            delete_stocks, insert_stocks, update_stocks = usd.find_insert_delete_update(fh_stock, db_stock_list)
            usd.create_global_queue(insert_stocks, update_stocks)
            exc = [exc for _ in range(len(api_objects))]
            workers = list(zip(cursor, api_objects, exc))
            usd.delete_stocks_from_db(cursor[0], delete_stocks, exc[0])
            with ThreadPoolExecutor(max_workers=len(workers)) as executor:
                executor.map(usd.insert_stocks_into_db, workers)
                executor.map(usd.update_stocks_into_db, workers)
            # For testing
            # usd.insert_stocks_into_db_test(cursor[0], api_objects, exc[0])
            # usd.update_stocks_into_db_test(cursor[0], api_objects, exc[0])
    usd.close_connection(connection, cursor)
    timer.stop()


if __name__ == "__main__":
    run_program()
