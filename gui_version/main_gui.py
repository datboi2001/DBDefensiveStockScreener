import connection as conn
import easygui as ez
import os
from pathlib import Path
from write_result_to_excel import create_file_path, write_to_excel_and_save


class StockScreener:
    def __init__(self):
        self.conn, self.curr = conn.create_connection()
        self.criteria = {"pe": "", "ps": "", "pb": "", "rg5y": "",
                         "current_price/high_price": "", 'roe': "", "exchange": ""}

    def start_gui(self):
        again = True
        while again:
            self._display_message("Welcome to Defensive Stock Screener, click Next to continue", "Next")
            self._display_message("Please choose where you want to save your results")
            dir_path = self._directory_chooser()
            if dir_path is None:
                break
            dir_path = Path(dir_path)
            file_name = self._enter_box("Please choose a file name (If nothing is entered, file name will be result)")
            file_path = create_file_path(file_name, dir_path)
            use_file_path = True
            result = []
            while use_file_path:
                fields, values = self._display_criteria()
                if values is None:
                    break
                while any(i == "" for i in values) or self.check_op_in_every_value(values):
                    fields, values = self._display_criteria()
                    if values is None:
                        break
                if values is None:
                    break
                self._add_values_to_criteria(fields, values)
                query = conn.create_query(self.criteria)
                result = conn.execute_query(self.curr, query)
                if result:
                    use_file_path = False
                else:
                    self._display_message("Nothing was found")
                    use_file_path = self._run_again(f"Do you want to use file path {file_path}")
            if result:
                write_to_excel_and_save(file_path, result)
                self._display_message(f"Results have been written to {file_path}")
                again = self._run_again("Do you want to run again?")
            else:
                again = False
        self._display_message("Thank you for using DefensiveStockScreener", "Exit")

    def check_op_in_every_value(self, values: [str]) -> bool:
        comparison = set(('>', '>=', '<', '<=', '='))
        if all(text != "US" for text in values):
            return True
        for text in values:
            if text.lower() != "any" and text != "US" and all(op not in text for op in comparison):
                return True
        return False

    def _add_values_to_criteria(self, fields: [str], values: [str]):
        for crit, value in zip(fields, values):
            self.criteria[crit] = value

    def _display_message(self, message: str, ok_button="Ok"):
        ez.msgbox(message, ok_button=ok_button)

    def _display_criteria(self) -> ([str], [str]):
        msg = "Enter your desired criteria (A comparison operator followed by a space followed by a value or Any if you don't want to use the criteria during the filtering.). For 'exchange', enter US for the US market."
        title = "Criteria dashboard"
        fields = sorted(self.criteria.keys())
        return fields, ez.multenterbox(msg, title, fields)

    def _run_again(self, msg: str) -> bool:
        return ez.ynbox(msg=msg)

    def stop_gui(self) -> None:
        conn.close_connection(self.conn, self.curr)

    def _directory_chooser(self) -> os.path:
        return ez.diropenbox(title="Choose your directory")

    def _enter_box(self, msg: str) -> str:
        return ez.enterbox(msg=msg, default="result")
