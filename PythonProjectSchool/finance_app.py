import tkinter as tk
import datetime
from PIL import Image, ImageTk


from data import DataManager, DataRecord
from login_manager import LoginManager
from tabs import TabsManager
from add_trans import AddTransaction
from pages import PagesManager


# ----------------- 1. Data Structure -----------------


class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Finance Tracker")
        self.geometry("410x700")
        self.config(bg="#1e1e1e")
        self.resizable(False, False)

        window_width, window_height = 410, 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height/ 2.1) - (window_height / 2))
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Files
        self.user_file = "users.json"
        self.data_file = "transactions.json"
        self.iconphoto(False, tk.PhotoImage(file="images/logo.png"))

        # ---------------- Data ----------------
        self.data = DataRecord()
        self.transactions = []
        self.goals = []
        self.monthly_goal = 0
        self.current_user = None


        self.current_date = datetime.date.today()
        self.top_tabs = ["Daily", "Calendar", "Monthly", "Budget", "Goals"]
        self.bottom_tabs = ["Trans.", "Stats", "Tax Calc.", "Account"]
        self.current_bottom_tab = "Trans."
        self.stats_view_mode = "Income"
        self.active_tab_index = 0

        # --- Date/Time Variables ---
        self.selected_datetime = datetime.datetime.now()
        self.date_var = tk.StringVar(value=self.selected_datetime.strftime("%d/%m/%Y"))
        self.time_var = tk.StringVar(value=self.selected_datetime.strftime("%I:%M %p"))
        self.stats_labels = {}

        self.tax_calc_mode_var = tk.StringVar(value="Yearly")  # default mode = yearly
        self.tax_income_var = tk.StringVar()
        self.tax_result_var = tk.StringVar(value="Press 'Calculate tax' to show the result")

        # Popup Variables
        self.popup_offset_x = 0
        self.popup_offset_y = 0
        self.current_add_type = "Income"  # Default

        # Login Frames
        self.add_trans = AddTransaction(self,TabsManager)
        self.login_manager = LoginManager(self, self.add_trans)
        self.tabs_manager = TabsManager(self,self.add_trans)
        self.pages_manager = PagesManager(self)



    # ---------------- Data Persistence (FIXED) ----------------
    def load_data(self):
        t, g, b, d = DataManager.load_user_data(self.current_user)
        self.transactions = t
        self.goals = g
        self.monthly_goal = b
        self.data = d

    def save_data(self):
        DataManager.save_user_data(
            self.current_user,
            self.transactions,
            self.goals,
            self.monthly_goal
        )


    # ---------------- Build UI (Unchanged) ----------------
    def build_ui(self):
        self.build_top_section()
        self.build_top_tabs()
        self.add_trans.build_add_button()
        self.build_stats_section()
        self.build_pages()
        self.build_bottom_nav()
        self.show_bottom_page("Trans.")

    def build_top_section(self):
        # Replaces original next_month/prev_month commands with change_date
        self.top_section = tk.Frame(self, bg="#2b2b2b", height=50)
        self.top_section.pack(fill="x")

        prev_btn = tk.Button(self.top_section, text="◀", bg="#2b2b2b", fg="white",
                             font=("Comic Sans MS", 14), bd=0, command=lambda: self.change_date(-1))
        prev_btn.pack(side="left", padx=15, pady=10)

        # month_label will be updated in update_month_label based on the active page
        self.month_label = tk.Label(self.top_section, text=self.current_date.strftime("%B %Y"),
                                    bg="#2b2b2b", fg="white", font=("Comic Sans MS", 15, "bold"))
        self.month_label.pack(side="left", expand=True)

        next_btn = tk.Button(self.top_section, text="▶", bg="#2b2b2b", fg="white",
                             font=("Comic Sans MS", 14), bd=0, command=lambda: self.change_date(1))
        next_btn.pack(side="right", padx=15, pady=10)

    def build_stats_section(self):
        self.stats_section = tk.Frame(self, bg="#1e1e1e")
        self.stats_section.pack(fill="x", pady=(5, 5))

        # Header labels for Income, Expenses, Total
        for i, name in enumerate(["Income", "Expenses", "Total"]):
            lbl = tk.Label(self.stats_section, text=name, fg="white", bg="#1e1e1e",
                           font=("Arial", 10))
            lbl.grid(row=0, column=i, padx=42)

        # Value labels below the headers
        self.stats_labels["Income"] = tk.Label(self.stats_section, fg="skyblue", bg="#1e1e1e",
                                               font=("Arial", 10, "bold"))
        self.stats_labels["Income"].grid(row=1, column=0)
        self.stats_labels["Expenses"] = tk.Label(self.stats_section, fg="red", bg="#1e1e1e",
                                                 font=("Arial", 10, "bold"))
        self.stats_labels["Expenses"].grid(row=1, column=1)
        self.stats_labels["Total"] = tk.Label(self.stats_section, fg="white", bg="#1e1e1e",
                                              font=("Arial", 10, "bold"))
        self.stats_labels["Total"].grid(row=1, column=2)

        self.update_stats()

    def build_pages(self):
        self.pages = []
        for tab_name in self.top_tabs:
            frame = tk.Frame(self, bg="#1e1e1e")

            if tab_name == "Daily":
                self.daily_page_frame = frame
            elif tab_name == "Calendar":
                self.calendar_page_frame = frame
            elif tab_name == "Monthly":
                self.monthly_page_frame = frame
            elif tab_name == "Budget":
                self.budget_page_frame = frame
            elif tab_name == "Goals":
                self.goals_page_frame = frame
            else:
                tk.Label(frame, text=f"This is {tab_name} page", fg="white", bg="#1e1e1e",
                         font=("Arial", 14)).pack(pady=80)
            self.pages.append(frame)

    def build_top_tabs(self):
        self.tabs_section = tk.Frame(self, bg="#1e1e1e")
        self.tabs_section.pack(fill="x", pady=(1, 1))

        for i in range(len(self.top_tabs)):
            self.tabs_section.columnconfigure(i, weight=1)

        self.top_tab_labels = []
        for i, tab in enumerate(self.top_tabs):
            label = tk.Label(self.tabs_section, text=tab, fg="white", bg="#1e1e1e",
                             font=("Microsoft YaHei", 10))
            label.grid(row=0, column=i, padx=5, pady=5)
            label.bind("<Button-1>", lambda e, idx=i: self.show_page(idx))
            self.top_tab_labels.append(label)

        self.active_line = tk.Frame(self.tabs_section, bg="#ff4444", height=2, width=40)
        self.active_line.grid(row=1, column=0, pady=(0, 3))

    def build_bottom_nav(self):
        self.bottom_frame = tk.Frame(self, bg="#2b2b2b", height=40)
        self.bottom_frame.pack(side="bottom", fill="x")

        for i in range(len(self.bottom_tabs)):
            self.bottom_frame.columnconfigure(i, weight=1)

        self.bottom_tab_labels = []
        self.colored_icons = {}
        icon_paths = {
            "Trans.": "images/trans.png",
            "Stats": "images/stats.png",
            "Tax Calc.": "images/account.png",
            "Account": "images/more.png"
        }

        # Load and color icons (red for active, white for inactive)
        for tab in self.bottom_tabs:
            try:
                img = Image.open(icon_paths[tab]).convert("RGBA").resize((24, 24))
                alpha = img.split()[-1]
                self.colored_icons[(tab, "white")] = ImageTk.PhotoImage(img)
                red_img = Image.new("RGBA", img.size, (255, 80, 80, 255))
                red_img.putalpha(alpha)
                self.colored_icons[(tab, "red")] = ImageTk.PhotoImage(red_img)
            except:
                self.colored_icons[(tab, "white")] = None
                self.colored_icons[(tab, "red")] = None

        for i, tab in enumerate(self.bottom_tabs):
            label = tk.Label(self.bottom_frame, text=tab, fg="white", bg="#2b2b2b",
                             font=("Microsoft YaHei", 10),
                             image=self.colored_icons.get((tab, "white")), compound="top")
            label.grid(row=0, column=i, padx=5, pady=5)
            label.bind("<Button-1>", lambda e, t=tab: self.on_bottom_tab_click(t))
            self.bottom_tab_labels.append(label)

        self.on_bottom_tab_click("Trans.")



    def change_date(self, delta):
        # 1. Determine Date Change Logic
        # Decide whether to change month or year based on the active top tab
        current_tab_name = self.top_tabs[self.active_tab_index]

        if current_tab_name == 'Monthly' and self.current_bottom_tab == "Trans.":
            # Special case: If viewing Annual Report on Trans page
            new_year = self.current_date.year + delta
            try:
                self.current_date = self.current_date.replace(year=new_year)
            except ValueError:
                self.current_date = self.current_date.replace(year=new_year, day=1)
        else:
            # Default: Change Month
            year, month = self.current_date.year, self.current_date.month + delta
            if month > 12:
                month = 1
                year += 1
            elif month < 1:
                month = 12
                year -= 1
            self.current_date = datetime.date(year, month, 1)

        # 2. Update the Text Label (e.g., "October 2023")
        self.update_month_label()

        # 3. Refresh Global Stats (The small bar: Income/Exp/Total)
        self.update_stats()

        # 4. Refresh Active Content based on which Bottom Tab is open
        if self.current_bottom_tab == "Trans.":
            # If on Home page, refresh the top tab content (Daily/Calendar/etc)
            self.refresh_active_page()

        elif self.current_bottom_tab == "Stats":
            # If on Stats page, refresh the stats list!
            self.pages_manager.update_stats_page()

        elif self.current_bottom_tab == "Monthly":
            self.tabs_manager.update_monthly_page()

    def update_month_label(self):
        # Set top label content based on the current page
        current_tab_name = self.top_tabs[self.active_tab_index]

        if current_tab_name == 'Monthly' and self.current_bottom_tab == "Trans.":
            # Display only the Year
            display_text = self.current_date.strftime("%Y")
        else:
            # Display Month and Year
            display_text = self.current_date.strftime("%B %Y")

        self.month_label.config(text=display_text)

    def next_month(self):
        year, month = self.current_date.year, self.current_date.month + 1
        if month > 12:
            month = 1
            year += 1

        # Update current date (set to first day of the month)
        self.current_date = datetime.date(year, month, 1)

        # Update specific pages
        self.pages_manager.update_stats_page()  # Refresh the Stats page immediately

        # Optional: Update other parts if they exist
        if hasattr(self, 'update_month_label'):
            self.update_month_label()
        if hasattr(self, 'update_stats'):
            self.update_stats()

    def prev_month(self):
        year, month = self.current_date.year, self.current_date.month - 1
        if month < 1:
            month = 12
            year -= 1

        self.current_date = datetime.date(year, month, 1)

        self.pages_manager.update_stats_page()  # Refresh the Stats page immediately

        if hasattr(self, 'update_month_label'):
            self.update_month_label()
        if hasattr(self, 'update_stats'):
            self.update_stats()

    def set_active_tab(self, index):
        self.active_tab_index = index
        self.active_line.grid_forget()
        self.active_line.grid(row=1, column=index, pady=(0, 5))

    def update_stats(self):
        # 1. Get current target year and month
        target_year = self.current_date.year
        target_month = self.current_date.month

        # 2. Calculate totals for the specific month
        monthly_income = 0.0
        monthly_expenses = 0.0

        for t in self.transactions:
            # Ensure we only calculate for the current user and valid dates
            # (Assuming self.transactions contains datetime objects for 'date')
            t_date = t['date']

            if t_date.year == target_year and t_date.month == target_month:
                if t['type'] == 'Income':
                    monthly_income += t['amount']
                elif t['type'] == 'Expenses':
                    monthly_expenses += t['amount']

        monthly_total = monthly_income - monthly_expenses

        # 3. Update UI Labels
        self.stats_labels["Income"].config(text=f"RM {monthly_income:,.2f}")
        self.stats_labels["Expenses"].config(text=f"RM {monthly_expenses:,.2f}")
        self.stats_labels["Total"].config(text=f"RM {monthly_total:,.2f}")

    def update_stats_visibility(self):
        # 1. Get current Top Tab name
        current_tab = self.top_tabs[self.active_tab_index]

        # 2. Logic Check
        if current_tab == "Monthly":
            # Hide Stats Section
            self.stats_section.pack_forget()
        else:
            # Show Stats Section
            try:
                self.stats_section.pack(fill="x", pady=(5, 5), after=self.tabs_section)
            except tk.TclError:
                self.stats_section.pack(fill="x", pady=(5, 5))

    def show_page(self, index):

        for page in self.pages:
            page.pack_forget()

        current_tab = self.top_tabs[index]
        self.pages[index].pack(expand=True, fill="both")
        self.set_active_tab(index)
        self.update_month_label()
        self.add_trans.update_add_button_visibility()
        self.update_stats_visibility()

        if current_tab == "Daily":
            self.tabs_manager.update_daily_page()
        elif current_tab == "Calendar":
            self.tabs_manager.update_calendar_page()
        elif current_tab == "Monthly":
            self.tabs_manager.update_monthly_page()
        elif current_tab == "Budget":
            self.tabs_manager.update_budget_page()
        elif current_tab == "Goals":
            self.tabs_manager.update_goals_page()

    def refresh_active_page(self):
        current_tab = self.top_tabs[self.active_tab_index]
        if current_tab == "Daily":
            self.tabs_manager.update_daily_page()
        elif current_tab == "Calendar":
            self.tabs_manager.update_calendar_page()
        elif current_tab == "Monthly":
            self.tabs_manager.update_monthly_page()
        elif current_tab == "Budget":
            self.tabs_manager.update_budget_page()
        elif current_tab == "Goals":
            self.tabs_manager.update_goals_page()



# ===================Page=============================

    def on_bottom_tab_click(self, tab_name):
        self.current_bottom_tab = tab_name
        for label, tab in zip(self.bottom_tab_labels, self.bottom_tabs):
            # Change icon color based on active tab
            if tab == tab_name:
                label.config(fg="red", image=self.colored_icons.get((tab, "red")))
            else:
                label.config(fg="white", image=self.colored_icons.get((tab, "white")))
        self.show_bottom_page(tab_name)

    def show_bottom_page(self, tab_name):
        for page in self.pages:
            page.pack_forget()
        if hasattr(self, "bottom_pages"):
            for frame in self.bottom_pages.values():
                frame.pack_forget()
        else:
            self.bottom_pages = {}

        self.update_month_label()
        self.add_trans.update_add_button_visibility()

        if tab_name == "Trans.":
            self.top_section.pack(fill="x", side="top")
            self.tabs_section.pack(fill="x", pady=(1, 1))
            self.stats_section.pack(fill="x", pady=(5, 5))
            self.show_page(0)  # Shows the Daily/Calendar/etc tabs


        elif tab_name == "Stats":
            self.top_section.pack(fill="x", side="top")
            self.tabs_section.pack_forget()
            self.stats_section.pack_forget()

            self.pages_manager.update_stats_page()
            self.bottom_pages["Stats"].pack(expand=True, fill="both")

        elif tab_name == "Tax Calc.":
            self.top_section.pack_forget()
            self.tabs_section.pack_forget()
            self.stats_section.pack_forget()

            self.pages_manager.update_calcTax_page()
            self.bottom_pages["Tax Calc."].pack(expand=True, fill="both")

        elif tab_name == "Account":
            self.top_section.pack_forget()
            self.tabs_section.pack_forget()
            self.stats_section.pack_forget()

            self.pages_manager.update_account_page()
            self.bottom_pages["Account"].pack(expand=True, fill="both")

