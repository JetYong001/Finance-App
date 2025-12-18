import tkinter as tk
from tkinter import ttk
import datetime
from calendar import monthrange

from utlis import extract_icon


class TabsManager:
    def __init__(self, project,add_trans):
        self.project = project
        self.popup = add_trans


    # ---------------- Daily Page Update (Modified to show amount only on far right) ---------------


    def update_daily_page(self):
        # 1. Clear current content
        for widget in self.project.daily_page_frame.winfo_children():
            widget.destroy()

        # 2. Filter transactions for the current month
        target_year = self.project.current_date.year
        target_month = self.project.current_date.month

        current_month_transactions = [
            t for t in self.project.transactions
            if t['date'].year == target_year and t['date'].month == target_month
        ]

        # 3. Check if data exists
        if not current_month_transactions:
            tk.Label(self.project.daily_page_frame, text="🧾", font=("Arial", 45), fg="#555555", bg="#1e1e1e").pack(pady=30)
            tk.Label(self.project.daily_page_frame, text="No data available.", fg="#666666", bg="#1e1e1e",
                     font=("Arial", 12)).pack()
            return

        # 4. Group by date
        grouped_transactions = {}
        for t in current_month_transactions:
            date_key = t['date'].date()
            if date_key not in grouped_transactions:
                grouped_transactions[date_key] = []
            grouped_transactions[date_key].append(t)

        # Sort dates descending (newest on top)
        sorted_dates = sorted(grouped_transactions.keys(), reverse=True)

        list_frame = tk.Frame(self.project.daily_page_frame, bg="#1e1e1e")
        list_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # 5. Loop through dates and generate UI
        for date_key in sorted_dates:
            transactions_of_day = grouped_transactions[date_key]

            # Calculate daily totals
            daily_income = sum(t['amount'] for t in transactions_of_day if t['type'] == 'Income')
            daily_expenses = sum(t['amount'] for t in transactions_of_day if t['type'] == 'Expenses')

            # --- Day Header ---
            day_header = tk.Frame(list_frame, bg="#1e1e1e", height=30)
            day_header.pack(fill="x", pady=(5, 1), padx=10)

            date_label = tk.Label(day_header,
                                  text=f"{date_key.day} {date_key.strftime('%a')} {date_key.strftime('%m.%Y')}",
                                  fg="#999999", bg="#1e1e1e", font=("Arial", 9, "bold"))
            date_label.pack(side="left", anchor="w")

            # Daily Expenses (Rightmost)
            if daily_expenses > 0:
                tk.Label(day_header, text=f"-RM {daily_expenses:.2f}",
                         fg="red",
                         bg="#1e1e1e", font=("Arial", 10, "bold")).pack(side="right", padx=(5, 0), anchor="e")

            # Daily Income (Left of Expenses)
            if daily_income > 0:
                tk.Label(day_header, text=f"+RM {daily_income:.2f}",
                         fg="skyblue",
                         bg="#1e1e1e", font=("Arial", 10, "bold")).pack(side="right", padx=(5, 10), anchor="e")

            # --- Transaction List for the Day ---
            # Sort transactions within the day by time (newest first)
            transactions_of_day.sort(key=lambda t: t['date'], reverse=True)

            for transaction in transactions_of_day:
                amount = transaction['amount']
                type_name = transaction['type']

                item_frame = tk.Frame(list_frame, bg="#252525", padx=10, pady=8)
                item_frame.pack(fill="x", pady=0)

                # Configure grid columns
                item_frame.grid_columnconfigure(0, weight=1)
                item_frame.grid_columnconfigure(1, weight=0)

                # Set amount text and color
                if type_name == "Income":
                    color = "skyblue"
                    amount_text = f"+RM {amount:.2f}"
                elif type_name == "Expenses":
                    color = "red"
                    amount_text = f"-RM {amount:.2f}"
                else:  # Transfer
                    color = "white"
                    amount_text = f"RM {amount:.2f}"

                # Amount (Right side)
                tk.Label(item_frame, text=amount_text, fg=color, bg="#252525",
                         font=("Arial", 10, "bold"), anchor="e").grid(row=0, column=1, padx=(10, 0), sticky="e")

                # Details (Left Side)
                if type_name == "Transfer":
                    icon = "↔️"
                    detail = "Transfer"
                    from_acc = transaction.get('account_from', '')
                    to_acc = transaction.get('account_to', '')
                    secondary_detail = f"{extract_icon(from_acc)} {from_acc.split(' ')[-1]} → {extract_icon(to_acc)} {to_acc.split(' ')[-1]}"
                else:
                    full_category = transaction.get('category', 'N/A')
                    icon = extract_icon(full_category)
                    detail = full_category.split(' ', 1)[-1] if ' ' in full_category else full_category

                    full_account = transaction.get('account', 'N/A')
                    secondary_detail = f"{extract_icon(full_account)} {full_account.split(' ', 1)[-1]}"

                detail_frame = tk.Frame(item_frame, bg="#252525")
                detail_frame.grid(row=0, column=0, sticky="w")

                tk.Label(detail_frame, text=icon, fg="white", bg="#252525",
                         font=("Arial", 12)).pack(side="left", padx=(0, 5), anchor="w")

                tk.Label(detail_frame, text=detail, fg="white", bg="#252525",
                         font=("Arial", 11, "bold")).pack(side="left", anchor="w")

                # Secondary Detail (Account or Transfer info)
                tk.Label(item_frame, text=secondary_detail, fg="#999999", bg="#252525",
                         font=("Arial", 9)).grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))


    def update_calendar_page(self):
        # 1. Clear previous calendar content
        for widget in self.project.calendar_page_frame.winfo_children():
            widget.destroy()

        # 2. Filter transactions for the currently selected month/year
        target_year = self.project.current_date.year
        target_month = self.project.current_date.month

        # Data aggregation: { day_number: {'income': 0, 'expense': 0} }
        daily_sums = {}

        for t in self.project.transactions:
            t_date = t['date'].date()
            if t_date.year == target_year and t_date.month == target_month:
                day = t_date.day
                if day not in daily_sums:
                    daily_sums[day] = {'income': 0.0, 'expense': 0.0}

                if t['type'] == 'Income':
                    daily_sums[day]['income'] += t['amount']
                elif t['type'] == 'Expenses':
                    daily_sums[day]['expense'] += t['amount']

        # 3. Create Grid Layout
        # Main container for the calendar grid
        cal_container = tk.Frame(self.project.calendar_page_frame, bg="#1e1e1e")
        cal_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Days of the week headers
        days_header = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days_header):
            tk.Label(cal_container, text=day, fg="#8E8E8E", bg="#1e1e1e", font=("Arial", 9)).grid(row=0, column=i,
                                                                                                  sticky="nsew",
                                                                                                  pady=(0, 5))

        # 4. Generate Days
        # monthrange returns (weekday_of_first_day, number_of_days)
        # weekday_of_first_day: 0=Mon, 6=Sun.
        # We need 0=Sun, 1=Mon... for our grid.
        first_weekday, num_days = monthrange(target_year, target_month)

        # Convert Python's Monday=0 to our Sunday=0 grid system
        # If first_weekday is 6 (Sun), start_col should be 0.
        # If first_weekday is 0 (Mon), start_col should be 1.
        start_col = (first_weekday + 1) % 7

        row = 1
        col = start_col

        for day_num in range(1, num_days + 1):
            # Create a frame for each day cell
            cell_frame = tk.Frame(cal_container, bg="#252525", width=1, height=1)
            cell_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

            # Highlight "Today"
            if (target_year == datetime.date.today().year and
                    target_month == datetime.date.today().month and
                    day_num == datetime.date.today().day):
                cell_frame.config(bg="#333333", highlightbackground="#2a9df4", highlightthickness=1)

            # Day Number Label (Top Left)
            tk.Label(cell_frame, text=str(day_num), fg="white", bg=cell_frame.cget("bg"),
                     font=("Arial", 10, "bold")).pack(anchor="nw", padx=3, pady=2)

            # Show Data if exists
            if day_num in daily_sums:
                inc = daily_sums[day_num]['income']
                exp = daily_sums[day_num]['expense']

                # Income (Blue)
                if inc > 0:
                    tk.Label(cell_frame, text=f"+RM{inc:.2f}", fg="#4fc3f7", bg=cell_frame.cget("bg"),
                             font=("Arial", 8)).pack(anchor="e", padx=2)
                # Expense (Red)
                if exp > 0:
                    tk.Label(cell_frame, text=f"-RM{exp:.2f}", fg="#ff5555", bg=cell_frame.cget("bg"),
                             font=("Arial", 8)).pack(anchor="e", padx=2)

            # Grid logic
            col += 1
            if col > 6:
                col = 0
                row += 1

        # Configure Grid Weights so cells expand evenly
        for i in range(7):
            cal_container.grid_columnconfigure(i, weight=1)
        # Assume max 6 weeks/rows
        for i in range(1, 8):
            cal_container.grid_rowconfigure(i, weight=1)


    def update_monthly_page(self):
        # 2. Clear previous content
        for widget in self.project.monthly_page_frame.winfo_children():
            widget.destroy()

        # 3. Data Setup
        target_year = self.project.current_date.year
        monthly_summary = {m: {'income': 0.0, 'expense': 0.0} for m in range(1, 13)}

        for t in self.project.transactions:
            if t['date'].year == target_year:
                m = t['date'].month
                if t['type'] == 'Income':
                    monthly_summary[m]['income'] += t['amount']
                elif t['type'] == 'Expenses':
                    monthly_summary[m]['expense'] += t['amount']

        # 4. Grid Container (Compact Layout)
        # Added padding (padx=12) to make the overall grid smaller
        grid_container = tk.Frame(self.project.monthly_page_frame, bg="#1e1e1e")
        grid_container.pack(fill="both", expand=True, padx=12, pady=15)

        # Configure columns (2 columns)
        grid_container.grid_columnconfigure(0, weight=1)
        grid_container.grid_columnconfigure(1, weight=1)

        # Configure rows (6 rows for 12 months)
        for r in range(6):
            grid_container.grid_rowconfigure(r, weight=1)

        # 5. Build Cards
        for m in range(1, 13):
            data = monthly_summary[m]
            income = data['income']
            expense = data['expense']
            balance = income - expense

            is_positive = balance >= 0
            status_color = "#4caf50" if is_positive else "#ff5252"
            card_bg = "#252525"

            row = (m - 1) // 2
            col = (m - 1) % 2

            month_name = datetime.date(target_year, m, 1).strftime("%b")

            # Card Container
            # increased padx/pady between cards to make them look smaller
            card_frame = tk.Frame(grid_container, bg=card_bg, highlightbackground="#1e1e1e", highlightthickness=1)
            card_frame.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

            # Left Color Strip (Thin)
            strip = tk.Frame(card_frame, bg=status_color, width=3)
            strip.pack(side="left", fill="y")

            # Content Area
            content_frame = tk.Frame(card_frame, bg=card_bg, padx=4)
            content_frame.pack(side="left", fill="both", expand=True)

            # Top Section: Month + Balance
            top_frame = tk.Frame(content_frame, bg=card_bg)
            top_frame.pack(fill="x", pady=(4, 0))

            # Font size 9
            tk.Label(top_frame, text=month_name, fg="white", bg=card_bg,
                     font=("Arial", 9, "bold")).pack(side="left")

            tk.Label(top_frame, text=f"{balance:,.0f}", fg=status_color, bg=card_bg,
                     font=("Arial", 9, "bold")).pack(side="right")

            # Bottom Section: Income + Expense
            bottom_frame = tk.Frame(content_frame, bg=card_bg)
            bottom_frame.pack(fill="x", pady=(1, 4))

            # Font size 7 (Very compact)
            inc_txt = f"▲{int(income)}" if income > 0 else "-"
            tk.Label(bottom_frame, text=inc_txt, fg="#4caf50", bg=card_bg,
                     font=("Arial", 7)).pack(side="left")

            exp_txt = f"▼{int(expense)}" if expense > 0 else "-"
            tk.Label(bottom_frame, text=exp_txt, fg="#ff5252", bg=card_bg,
                     font=("Arial", 7)).pack(side="right")


    def update_budget_page(self):
        for widget in self.project.budget_page_frame.winfo_children():
            widget.destroy()

        current_expense = 0.0
        target_year = self.project.current_date.year
        target_month = self.project.current_date.month

        for t in self.project.transactions:
            if t['type'] == 'Expenses':
                if t['date'].year == target_year and t['date'].month == target_month:
                    current_expense += t['amount']

        limit = self.project.monthly_goal
        percent = (current_expense / limit * 100) if limit > 0 else 0

        if percent >= 100:
            bar_color = "#ff5555"  # Red
            status_text = "Over Budget!"
        elif percent >= 80:
            bar_color = "#ff9800"  # Orange
            status_text = "Warning"
        else:
            bar_color = "#4caf50"  # Green
            status_text = "On Track"

        container = tk.Frame(self.project.budget_page_frame, bg="#1e1e1e")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        card = tk.Frame(container, bg="#2b2b2b", padx=20, pady=20)
        card.pack(fill="x")

        header = tk.Frame(card, bg="#2b2b2b")
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text=f"{self.project.current_date.strftime('%B')} Budget", fg="#aaaaaa", bg="#2b2b2b",
                 font=("Arial", 12)).pack(side="left")
        tk.Label(header, text=status_text, fg=bar_color, bg="#2b2b2b", font=("Arial", 10, "bold")).pack(side="right")

        tk.Label(card, text=f"RM {limit:,.2f}", fg="white", bg="#2b2b2b", font=("Arial", 28, "bold")).pack(anchor="w")

        # Progress Bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Budget.Horizontal.TProgressbar", troughcolor="#404040", background=bar_color,
                        bordercolor="#2b2b2b", lightcolor=bar_color, darkcolor=bar_color)
        pb = ttk.Progressbar(card, style="Budget.Horizontal.TProgressbar", orient="horizontal", length=100,
                             mode="determinate", value=min(percent, 100))
        pb.pack(fill="x", pady=15)

        info = tk.Frame(card, bg="#2b2b2b")
        info.pack(fill="x")
        tk.Label(info, text=f"Spent: {current_expense:,.2f}", fg="#ff5555", bg="#2b2b2b").pack(side="left")

        remaining = limit - current_expense
        remain_color = "white" if remaining >= 0 else "#ff5555"
        tk.Label(info, text=f"Left: {remaining:,.2f}", fg=remain_color, bg="#2b2b2b").pack(side="right")

        # Edit Button
        tk.Frame(card, height=1, bg="#404040").pack(fill="x", pady=(15, 10))
        tk.Button(card, text="✎ Edit Budget Limit", bg="#333333", fg="white", font=("Arial", 12), relief="flat",
                  pady=12,
                  command=self.popup.open_edit_budget_popup).pack(fill="x")


    def update_goals_page(self):
        for widget in self.project.goals_page_frame.winfo_children():
            widget.destroy()

        goals_frame = tk.Frame(self.project.goals_page_frame, bg="#1e1e1e", highlightthickness=0)
        goals_frame.pack(side="left", fill="both", expand=True)

        # Add Button
        tk.Button(goals_frame, text="+ Add New Goal", bg="#2a9df4", fg="white", font=("Arial", 12, "bold"),
                  relief="flat", pady=10,
                  command=self.popup.open_add_goal_popup).pack(fill="x", padx=15, pady=15)

        if not self.project.goals:
            tk.Label(goals_frame, text="No goals set yet.", fg="#666", bg="#1e1e1e").pack(pady=20)

        for i, goal in enumerate(self.project.goals):
            self.create_goal_card(goals_frame, i, goal)


    def create_goal_card(self, parent, index, goal):
        card = tk.Frame(parent, bg="#2b2b2b", padx=15, pady=15)
        card.pack(fill="x", padx=15, pady=5)

        # Header: Name + Dateline
        header = tk.Frame(card, bg="#2b2b2b")
        header.pack(fill="x")
        tk.Label(header, text=goal['name'], fg="white", bg="#2b2b2b", font=("Arial", 13, "bold")).pack(side="left")

        try:
            deadline = datetime.datetime.strptime(goal['deadline'], "%Y-%m-%d").date()
            days_left = (deadline - datetime.date.today()).days
            if days_left < 0:
                d_text, d_col = "Expired", "#ff5555"
            else:
                d_text = f"{days_left} days left"
                d_col = "#ff9800" if days_left < 30 else "#4caf50"
        except:
            d_text, d_col = "No Date", "#888"

        tk.Label(header, text=d_text, fg=d_col, bg="#2b2b2b", font=("Arial", 10)).pack(side="right")

        # Progress
        target = float(goal['target'])
        saved = float(goal['saved'])
        percent = (saved / target * 100) if target > 0 else 0

        tk.Label(card, text=f"Saved: RM {saved:,.0f} / {target:,.0f}", fg="#aaaaaa", bg="#2b2b2b",
                 font=("Arial", 10)).pack(anchor="w", pady=(5, 2))

        style_name = f"Goal{index}.Horizontal.TProgressbar"
        style = ttk.Style()
        style.configure(style_name, troughcolor="#404040", background="#2a9df4", bordercolor="#2b2b2b")
        pb = ttk.Progressbar(card, style=style_name, orient="horizontal", length=100, mode="determinate",
                             value=min(percent, 100))
        pb.pack(fill="x", pady=5)

        # Buttons
        btns = tk.Frame(card, bg="#2b2b2b")
        btns.pack(fill="x", pady=(5, 0))

        tk.Button(btns, text="💰 Deposit", bg="#4caf50", fg="white", bd=0, padx=10,
                  command=lambda i=index: self.popup.open_deposit_popup(i)).pack(side="left")

        tk.Button(btns, text="🗑", bg="#ff5555", fg="white", bd=0, padx=10,
                  command=lambda i=index: self.popup.delete_goal(i)).pack(side="right")