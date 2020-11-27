from main_gui import StockScreener


def run_gui() -> None:
    app = StockScreener()
    app.start_gui()
    app.stop_gui()


if __name__ == "__main__":
    run_gui()