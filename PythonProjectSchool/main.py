from splash import SplashApp
from finance_app import FinanceApp


def main_app():
    root = FinanceApp()
    root.mainloop()


if __name__ == "__main__":
    app = SplashApp(on_complete_callback=main_app)
    app.mainloop()