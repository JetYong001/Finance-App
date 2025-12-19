import tkinter as tk
import datetime
from tkinter import messagebox
from calendar import monthrange
import pygame



class AddTransaction:
    def __init__(self, project,tabs_manager):
        self.project = project
        self.tabs_manager = tabs_manager
        pygame.mixer.init()


# ----------------------- Add Transaction Page -----------------------
    def play_sound(self):
        try:
            pygame.mixer.music.load("sound_effect/laicailaicai.mpeg")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error: {e}")

    def two_dollars_sound(self):
        try:
            pygame.mixer.music.load("sound_effect/two_dollars.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error: {e}")

    def build_add_button(self):
        self.add_btn = tk.Button(self.project, text="+", bg="#ff5555", fg="white", font=("Arial", 20, "bold"),
                                 bd=0, relief="flat", activebackground="#ff7777",
                                 activeforeground="white", command=self.add_two_function)

        self.update_add_button_visibility()

    def update_add_button_visibility(self):
        if not hasattr(self, 'add_btn'):
            return

        current_tab = self.project.top_tabs[self.project.active_tab_index]
        current_page = self.project.current_bottom_tab

        if current_tab == 'Monthly' or current_page == "Stats" or current_page == "Tax Calc." or current_page == "Account":
            self.add_btn.place_forget()
        else:
            self.add_btn.place(relx=0.89, rely=0.85, anchor="center", width=50, height=50)
            self.add_btn.lift()

    def show_add_transaction_page(self):
        sections_to_hide = [
            self.project.top_section,
            self.project.tabs_section,
            self.project.stats_section,
            *self.project.pages,
            *self.project.bottom_pages.values(),
            self.project.bottom_frame
        ]

        # Hide main UI elements
        for section in sections_to_hide:
            if section.winfo_manager():
                section.pack_forget()

        # Create the add transaction page
        self.project.add_page = tk.Frame(self.project, bg="#1e1e1e")
        self.project.add_page.pack(expand=True, fill="both")

        # Top line setup
        top_line = tk.Frame(self.project.add_page, bg="#1e1e1e")
        top_line.pack(fill="x", pady=10)

        back_btn = tk.Button(
            top_line, text="<", fg="white", bg="#1e1e1e",
            bd=0, relief="flat", font=("Arial", 15),
            command=self.close_add_page
        )
        back_btn.pack(side="left", padx=10)

        title_label = tk.Label(
            top_line, text="Add Transaction", fg="white", bg="#1e1e1e",
            font=("Arial", 12, "bold")
        )
        title_label.pack(side="left")

        # --- Buttons Section: Income/Expenses/Transfer ---
        buttons_frame = tk.Frame(self.project.add_page, bg="#1e1e1e")
        buttons_frame.pack(fill="x", pady=15)

        self.type_colors = {
            "Income": "#2a9df4",
            "Expenses": "#FF0000",
            "Transfer": "white"
        }

        self.default_border = "#333333"
        self.default_text = "#8E8E8E"
        self.type_buttons = {}

        # ------Data + Time Display------
        date_frame = tk.Frame(self.project.add_page, bg="#1e1e1e")
        date_frame.pack(fill="x", padx=15, pady=(0, 10))

        tk.Label(date_frame, text="Date", fg="white", bg="#1e1e1e",
                 font=("Arial", 11)).pack(anchor="w")

        # Container for the interactive date/time box
        date_box_frame = tk.Frame(date_frame, bg="#1e1e1e")
        date_box_frame.pack(fill="x", pady=5)

        # Date part (Clickable -> open date calendar)
        self.date_display = tk.Label(date_box_frame, textvariable=self.project.date_var,
                                     fg="#cfcfcf", bg="#1e1e1e", anchor="w", font=("Arial", 12))
        self.date_display.pack(side="left", padx=(0, 10))
        self.date_display.bind("<Button-1>", self.open_datetime_popup)

        # Time part (Clickable -> open time spinner)
        self.time_display = tk.Label(date_box_frame, textvariable=self.project.time_var,
                                     fg="#cfcfcf", bg="#1e1e1e", anchor="w", font=("Arial", 12))
        self.time_display.pack(side="left")
        self.time_display.bind("<Button-1>", self.open_time_popup)

        tk.Frame(date_frame, bg="#333333", height=1).pack(fill="x")

        # =========Amount Input ============
        amount_frame = tk.Frame(self.project.add_page, bg="#1e1e1e")
        amount_frame.pack(fill="x", padx=15, pady=(10, 0))

        tk.Label(amount_frame, text="Amount", fg="white", bg="#1e1e1e",
                 font=("Arial", 11)).pack(anchor="w")

        entry_container = tk.Frame(amount_frame, bg="#1e1e1e")
        entry_container.pack(fill="x", pady=5)

        tk.Label(entry_container, text="RM", fg="white", bg="#1e1e1e",
                 font=("Arial", 12)).pack(side="left")

        # Set default value to empty string
        self.amount_var = tk.StringVar(value="")

        amount_box = tk.Entry(
            entry_container, textvariable=self.amount_var,
            fg="#cfcfcf", bg="#1e1e1e", insertbackground="white",
            font=("Arial", 12), bd=0
        )
        amount_box.pack(side="left", fill="x", expand=True)
        tk.Frame(amount_frame, bg="#333333", height=1).pack(fill="x")

        # ========= Dynamic Rows (Category/Account fields) ============
        self.category_var = tk.StringVar(value="")
        self.money_type_var = tk.StringVar(value="")

        # Helper to create an input line (label + display/entry)
        def create_line_input(label_text, var_obj=None):
            frame = tk.Frame(self.project.add_page, bg="#1e1e1e")
            frame.pack(fill="x", padx=10, pady=(10, 0))

            lbl_widget = tk.Label(frame, text=label_text, fg="white", bg="#1e1e1e",
                                  font=("Arial", 11))
            lbl_widget.pack(anchor="w")

            if var_obj is not None:
                # Display label for selection popups
                display = tk.Label(
                    frame, textvariable=var_obj, fg="#cfcfcf", bg="#1e1e1e",
                    anchor="w", font=("Arial", 12)
                )
                display.pack(fill="x", pady=5, padx=3)
                tk.Frame(frame, bg="#333333", height=1).pack(fill="x")
                return lbl_widget, display
            else:
                # Normal Entry for notes
                entry = tk.Entry(
                    frame, fg="#cfcfcf", bg="#1e1e1e",
                    insertbackground="white", font=("Arial", 12), bd=0
                )
                entry.pack(fill="x", pady=5, padx=3)
                tk.Frame(frame, bg="#333333", height=1).pack(fill="x")
                return lbl_widget, entry

        # Row 1 (Category or From account)
        self.row1_label, self.row1_input = create_line_input("Category", self.category_var)

        # Row 2 (Money Types or To account)
        self.row2_label, self.row2_input = create_line_input("Money Types", self.money_type_var)

        # Row 3 (Note)
        _, self.note_input = create_line_input("Note")

        # ======= Save and Continue Buttons =========
        bottom_btn_frame = tk.Frame(self.project.add_page, bg="#1e1e1e")
        bottom_btn_frame.pack(fill="x", padx=10, pady=10)
        bottom_btn_frame.columnconfigure(0, weight=3)
        bottom_btn_frame.columnconfigure(1, weight=1)

        self.save_btn = tk.Button(
            bottom_btn_frame, text="Save", fg="white",
            bg=self.type_colors["Income"], font=("Arial", 10),
            height=2, relief="flat",
            command=self.save_two_function
        )
        self.save_btn.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        continue_btn = tk.Button(
            bottom_btn_frame, text="Continue", fg="white",
            bg="#333333", font=("Arial", 10), height=2, relief="flat"
        )
        continue_btn.grid(row=0, column=1, sticky="nsew")

        # ----- Selection Logic -----
        def select_button(clicked):
            # Reset all buttons
            for c in self.type_buttons.values():
                c.itemconfig(c.rect, outline=self.default_border)
                c.itemconfig(c.txt, fill=self.default_text)

            # Set active button color and type
            self.project.current_add_type = clicked.label
            color = self.type_colors[self.project.current_add_type]
            clicked.itemconfig(clicked.rect, outline=color)
            clicked.itemconfig(clicked.txt, fill=color)

            # Clear selection variables
            self.category_var.set("")
            self.money_type_var.set("")

            # Update save button look
            self.save_btn.config(bg=color)

            if self.project.current_add_type == "Transfer":
                self.save_btn.config(fg="black")
                # Change UI for Transfer
                self.row1_label.config(text="From")
                self.row2_label.config(text="To")
                self.row1_input.bind("<Button-1>", lambda e: self.open_moneytype_popup(self.category_var))
                self.row2_input.bind("<Button-1>", lambda e: self.open_moneytype_popup(self.money_type_var))

            else:
                self.save_btn.config(fg="white")
                # Change UI for Income/Expenses
                self.row1_label.config(text="Category")
                self.row2_label.config(text="Money Types")
                self.row1_input.bind("<Button-1>", lambda e: self.open_category_popup())
                self.row2_input.bind("<Button-1>", lambda e: self.open_moneytype_popup(self.money_type_var))

        # ----- Create the Canvas Buttons -----
        def make_button(parent, text):
            canvas = tk.Canvas(parent, width=120, height=40, bg="#1e1e1e", highlightthickness=0)
            rect = canvas.create_rectangle(0, 0, 120, 40, outline=self.default_border, width=2)
            txt = canvas.create_text(59, 20, text=text, fill=self.default_text)
            canvas.rect = rect
            canvas.txt = txt
            canvas.label = text
            canvas.bind("<Button-1>", lambda e: select_button(canvas))
            return canvas

        for name in ["Income", "Expenses", "Transfer"]:
            btn = make_button(buttons_frame, name)
            btn.pack(side="left", padx=8)
            self.type_buttons[name] = btn

        # Default to Income
        select_button(self.type_buttons["Income"])

    def close_add_page(self):
        # Hide add page and show previous elements
        self.project.add_page.pack_forget()
        self.project.add_page.destroy()
        self.project.bottom_frame.pack(side="bottom", fill="x")
        if self.project.current_bottom_tab == "Trans.":
            self.project.top_section.pack(fill="x")
            self.project.tabs_section.pack(fill="x", pady=(1, 1))
            self.project.stats_section.pack(fill="x", pady=(5, 5))
            self.project.tabs_manager.update_calendar_page()
            self.project.pages[self.project.active_tab_index].pack(expand=True, fill="both")
        else:
            if self.project.current_bottom_tab in self.project.bottom_pages:
                self.project.bottom_pages[self.project.current_bottom_tab].pack(expand=True, fill="both")

    def save_two_function(self):
        self.play_sound()
        self.save_transaction()

    def add_two_function(self):
        self.two_dollars_sound()
        self.update_add_button_visibility()
        self.show_add_transaction_page()



# --------------- Popups (Date/Time/Category/Account) ----------------

    def open_add_goal_popup(self):
        popup = tk.Toplevel(self.project)
        popup.title("New Goal")
        self.center_popup(popup, 300, 300)
        popup.config(bg="#2b2b2b")

        def entry_field(lbl):
            tk.Label(popup, text=lbl, fg="#aaaaaa", bg="#2b2b2b").pack(anchor="w", padx=20, pady=(10, 0))
            e = tk.Entry(popup, bg="#444", fg="white", insertbackground="white")
            e.pack(fill="x", padx=20, pady=5)
            return e

        name_e = entry_field("Goal Name")
        target_e = entry_field("Target Amount (RM)")
        date_e = entry_field("Deadline (YYYY-MM-DD)")
        date_e.insert(0, datetime.date.today().strftime("%Y-%m-%d"))


        def save():
            try:
                nm = name_e.get()
                amt = float(target_e.get())
                dt = date_e.get()
                datetime.datetime.strptime(dt, "%Y-%m-%d")  # Validate date

                self.project.goals.append({"name": nm, "target": amt, "saved": 0.0, "deadline": dt})
                self.project.save_data()
                self.project.tabs_manager.update_goals_page()
                popup.destroy()
            except:
                messagebox.showerror("Error", "Invalid Amount or Date format")

        tk.Button(popup, text="Create", bg="#2a9df4", fg="white", command=save, pady=5).pack(fill="x", padx=20, pady=20)

    def open_deposit_popup(self, index):
        popup = tk.Toplevel(self.project)
        popup.title("Deposit")
        self.center_popup(popup, 250, 150)
        popup.config(bg="#2b2b2b")

        tk.Label(popup, text=f"Add to {self.project.goals[index]['name']}:", fg="white", bg="#2b2b2b").pack(pady=10)
        e = tk.Entry(popup)
        e.pack(pady=5)
        e.focus()

        def confirm():
            try:
                amt = float(e.get())
                self.project.goals[index]['saved'] += amt
                self.project.save_data()
                self.project.tabs_manager.update_goals_page()
                popup.destroy()
            except:
                pass

        tk.Button(popup, text="Confirm", bg="#4caf50", fg="white", command=confirm).pack(pady=10)

    def delete_goal(self, index):
        if messagebox.askyesno("Confirm", "Delete this goal?"):
            del self.project.goals[index]
            self.project.save_data()
            self.project.tabs_manager.update_goals_page()

    # --- Budget ---

    def open_edit_budget_popup(self):
        popup = tk.Toplevel(self.project)
        popup.title("Set Budget")
        self.center_popup(popup, 300, 150)
        popup.config(bg="#2b2b2b")

        tk.Label(popup, text="Monthly Limit (RM):", fg="white", bg="#2b2b2b").pack(pady=15)
        entry = tk.Entry(popup, font=("Arial", 14), justify="center")
        entry.insert(0, str(int(self.project.monthly_goal)))
        entry.pack(fill="x", padx=30)
        entry.focus()

        def save():
            try:
                self.project.monthly_goal = float(entry.get())
                self.project.save_data()
                self.project.tabs_manager.update_budget_page()
                popup.destroy()
            except:
                messagebox.showerror("Error", "Invalid Number")

        tk.Button(popup, text="Save", bg="#2a9df4", fg="white", command=save, relief="flat").pack(pady=15)

    # --- Date Selection Popup (Calendar Style) ---

    def open_datetime_popup(self, event=None):
        if hasattr(self, "dt_popup") and self.dt_popup.winfo_exists():
            return

        self.calendar_month_date = self.project.selected_datetime.replace(day=1).date()

        popup = tk.Toplevel(self.project)
        self.dt_popup = popup
        popup.configure(bg="#2b2b2b")
        popup.overrideredirect(True)
        popup.grab_set()

        self.center_popup(popup, 300, 420)

        self.project.bind("<Configure>", self.update_popup_position)

        # --- Top Display (e.g., "2025 Tue, 25 Nov") ---
        display_frame = tk.Frame(popup, bg="#333333", height=100)
        display_frame.pack(fill="x")

        self.popup_year_label = tk.Label(display_frame, text=self.project.selected_datetime.strftime("%Y"),
                                         fg="#999999", bg="#333333", font=("Arial", 14))
        self.popup_year_label.pack(anchor="w", padx=20, pady=(15, 0))

        self.popup_date_label = tk.Label(display_frame, text=self.project.selected_datetime.strftime("%a, %d %b"),
                                         fg="white", bg="#333333", font=("Arial", 20, "bold"))
        self.popup_date_label.pack(anchor="w", padx=20, pady=(0, 15))

        # --- Calendar Controls ---
        calendar_body = tk.Frame(popup, bg="#2b2b2b")
        calendar_body.pack(fill="both", expand=True)

        self.calendar_frame_inner = tk.Frame(calendar_body, bg="#2b2b2b")
        self.calendar_frame_inner.pack(pady=10)

        def update_date_display(dt):
            self.popup_year_label.config(text=dt.strftime("%Y"))
            self.popup_date_label.config(text=dt.strftime("%a, %d %b"))
            self.project.date_var.set(dt.strftime("%d/%m/%Y"))

        def change_month(delta):
            y, m = self.calendar_month_date.year, self.calendar_month_date.month + delta
            if m > 12:
                m, y = 1, y + 1
            elif m < 1:
                m, y = 12, y - 1
            self.calendar_month_date = self.calendar_month_date.replace(year=y, month=m, day=1)
            render_calendar()

        def select_date(date_obj):
            self.project.selected_datetime = datetime.datetime.combine(date_obj, self.project.selected_datetime.time())
            update_date_display(self.project.selected_datetime)
            render_calendar()

        def render_calendar():
            for widget in self.calendar_frame_inner.winfo_children():
                widget.destroy()

            # Month Navigation (Scroll Wheel Style)
            nav_frame = tk.Frame(self.calendar_frame_inner, bg="#2b2b2b")
            nav_frame.pack(fill="x", pady=5)

            tk.Button(nav_frame, text="<", fg="white", bg="#2b2b2b", activebackground="#2b2b2b", bd=0,
                      font=("Arial", 12), command=lambda: change_month(-1)).pack(side="left", padx=10)

            tk.Label(nav_frame, text=self.calendar_month_date.strftime("%B %Y"),
                     fg="white", bg="#2b2b2b", font=("Arial", 12)).pack(side="left", expand=True)

            tk.Button(nav_frame, text=">", fg="white", bg="#2b2b2b", activebackground="#2b2b2b", bd=0,
                      font=("Arial", 12), command=lambda: change_month(1)).pack(side="right", padx=10)

            # Weekday Headers
            days = ["S", "M", "T", "W", "T", "F", "S"]
            days_frame = tk.Frame(self.calendar_frame_inner, bg="#2b2b2b")
            days_frame.pack(fill="x", padx=10, pady=(5, 0))
            for i, day in enumerate(days):
                tk.Label(days_frame, text=day, fg="#999999", bg="#2b2b2b", font=("Arial", 10)).grid(row=0, column=i,
                                                                                                    padx=5, pady=2)

            # Calendar Grid
            grid_frame = tk.Frame(self.calendar_frame_inner, bg="#2b2b2b")
            grid_frame.pack(fill="both", expand=True, padx=10)

            first_day_of_week = self.calendar_month_date.weekday()
            first_day_col = first_day_of_week + 1 if first_day_of_week < 6 else 0

            num_days = monthrange(self.calendar_month_date.year, self.calendar_month_date.month)[1]

            row, col = 1, first_day_col

            for day_num in range(1, num_days + 1):
                date_to_check = self.calendar_month_date.replace(day=day_num)

                bg_color = "#2b2b2b"
                fg_color = "white"

                if date_to_check == self.project.selected_datetime.date():
                    bg_color = "#6693f5"
                    fg_color = "white"
                elif date_to_check == datetime.date.today():
                    fg_color = "#6693f5"

                btn = tk.Button(
                    grid_frame, text=str(day_num), fg=fg_color, bg=bg_color,
                    width=4, height=1, relief="flat", bd=0, activebackground="#444444",
                    command=lambda dt=date_to_check: select_date(dt)
                )
                btn.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

                col += 1
                if col > 6:
                    col = 0
                    row += 1

            for c in range(7):
                grid_frame.grid_columnconfigure(c, weight=1)

        # Action Buttons
        button_frame = tk.Frame(popup, bg="#2b2b2b")
        button_frame.pack(fill="x", pady=(0, 5))

        tk.Button(button_frame, text="OK", fg="#6693f5", bg="#2b2b2b", bd=0, relief="flat",
                  activebackground="#444444", font=("Arial", 11, "bold"),
                  command=self.dt_popup.destroy).pack(side="right", padx=15, pady=5)

        tk.Button(button_frame, text="CANCEL", fg="#999999", bg="#2b2b2b", bd=0, relief="flat",
                  activebackground="#444444", font=("Arial", 11, "bold"),
                  command=lambda: [self.dt_popup.destroy()]).pack(side="right", pady=5)

        render_calendar()

    # --- Time Selection Popup (Spinner Style) ---

    def open_time_popup(self, event=None):
        if hasattr(self, "time_popup") and self.time_popup.winfo_exists():
            return

        current_dt = self.project.selected_datetime

        popup = tk.Toplevel(self.project)
        self.time_popup = popup
        popup.configure(bg="#2b2b2b")
        popup.overrideredirect(True)
        popup.grab_set()

        self.center_popup(popup, 220, 150)

        self.project.bind("<Configure>", self.update_popup_position)

        self.time_entry_vars = [tk.StringVar(value=current_dt.strftime("%I")),  # Hour
                                tk.StringVar(value=current_dt.strftime("%M")),  # Minute
                                tk.StringVar(value=current_dt.strftime("%p"))]  # AM/PM

        time_frame = tk.Frame(popup, bg="#2b2b2b")
        time_frame.pack(fill="x", expand=True, pady=20)

        def adjust(var_index, delta, range_min, range_max, wrap=False):
            var = self.time_entry_vars[var_index]
            try:
                current = int(var.get())
            except ValueError:
                current = range_min

            new_value = current + delta

            if wrap:
                if new_value > range_max:
                    new_value = range_min
                elif new_value < range_min:
                    new_value = range_max
            else:
                new_value = max(range_min, min(range_max, new_value))

            var.set(f"{new_value:02d}")
            update_time_from_spinners()

        def create_time_spinner(parent, var_index, range_min, range_max, step, wrap=False):
            var = self.time_entry_vars[var_index]
            spinner = tk.Frame(parent, bg="#2b2b2b")

            tk.Button(spinner, text="▲", fg="white", bg="#333333", bd=0, relief="flat",
                      command=lambda: adjust(var_index, step, range_min, range_max, wrap)).pack(fill="x")

            tk.Entry(spinner, textvariable=var, width=3, font=("Arial", 16, "bold"),
                     bg="#2b2b2b", fg="white", justify="center", bd=0,
                     insertbackground="white").pack(pady=2)

            tk.Button(spinner, text="▼", fg="white", bg="#333333", bd=0, relief="flat",
                      command=lambda: adjust(var_index, -step, range_min, range_max, wrap)).pack(fill="x")

            return spinner

        create_time_spinner(time_frame, 0, 1, 12, 1, wrap=True).pack(side="left", padx=10)

        tk.Label(time_frame, text=":", fg="white", bg="#2b2b2b", font=("Arial", 20)).pack(side="left")

        create_time_spinner(time_frame, 1, 0, 59, 1, wrap=True).pack(side="left", padx=10)

        def toggle_ampm():
            current = self.time_entry_vars[2].get()
            new = "AM" if current == "PM" else "PM"
            self.time_entry_vars[2].set(new)
            update_time_from_spinners()

        ampm_btn = tk.Button(
            time_frame, textvariable=self.time_entry_vars[2], fg="white", bg="#333333",
            font=("Arial", 12, "bold"), width=5, height=1, relief="flat",
            command=toggle_ampm
        )
        ampm_btn.pack(side="left", padx=10)

        def update_time_from_spinners(*args):
            try:
                hour = int(self.time_entry_vars[0].get())
                minute = int(self.time_entry_vars[1].get())
                ampm = self.time_entry_vars[2].get()

                if ampm == "PM" and hour != 12:
                    hour += 12
                elif ampm == "AM" and hour == 12:
                    hour = 0

                new_time = datetime.time(hour, minute)
                self.project.selected_datetime = datetime.datetime.combine(self.project.selected_datetime.date(), new_time)

                self.project.time_var.set(self.project.selected_datetime.strftime("%I:%M %p"))

            except ValueError:
                pass

        tk.Button(popup, text="OK", fg="white", bg="#6693f5", font=("Arial", 10, "bold"),
                  relief="flat", height=1, command=popup.destroy).pack(fill="x", ipady=5)

        self.time_entry_vars[0].trace_add("write", update_time_from_spinners)
        self.time_entry_vars[1].trace_add("write", update_time_from_spinners)

    # --- General Popups ---
    def open_category_popup(self):
        # Category selection popup
        if hasattr(self, "category_popup") and self.category_popup.winfo_exists():
            self.category_popup.destroy()

        popup = tk.Toplevel(self.project)
        self.category_popup = popup
        popup.configure(bg="#1e1e1e")
        popup.overrideredirect(True)
        popup.grab_set()

        w, h = 406, 290
        self.project.popup_offset_x = 10
        self.project.popup_offset_y = self.project.winfo_height() - h - 20

        popup.geometry(f"{w}x{h}+{self.project.winfo_x() + self.project.popup_offset_x}"
                       f"+{self.project.winfo_y() + self.project.popup_offset_y}")

        top_bar = tk.Frame(popup, bg="#5d5d5d")
        top_bar.pack(fill="x")
        close_btn = tk.Button(
            top_bar, text="x", fg="white", bg="#5d5d5d",
            relief="flat", bd=0, font=("Arial", 15), command=popup.destroy
        )
        close_btn.pack(side="right", padx=5)

        if self.project.current_add_type == "Income":
            categories = [
                ("💰", "Allowance"), ("💵", "Salary"), ("🎁", "Bonus"),
                ("⭐", "Other")
            ]

        else:
            categories = [
                ("🍔", "Food"), ("🧑‍🤝‍🧑", "Social Life"), ("🐶", "Pets"),
                ("🚗", "Transport"), ("🎭", "Culture"), ("🏠", "Household"),
                ("👕", "Apparel"), ("💄", "Beauty"), ("🩺", "Health"),
                ("📚", "Education"), ("🎁", "Gift"), ("⚙️", "Other")
            ]

        grid = tk.Frame(popup, bg="#1e1e1e")
        grid.pack(pady=15)

        def select_cat(icon, name):
            self.category_var.set(f"{icon} {name}")
            popup.destroy()

        for i, (icon, name) in enumerate(categories):
            tk.Button(
                grid, text=f"{icon}  {name}", font=("Arial", 10),
                fg="white", bg="#333333", width=13, height=2,
                relief="flat", command=lambda ic=icon, nm=name: select_cat(ic, nm)
            ).grid(row=i // 3, column=i % 3, padx=5, pady=5)

    def open_moneytype_popup(self, target_var):
        # Account/Money Type selection popup
        if hasattr(self, "moneytype_popup") and self.moneytype_popup.winfo_exists():
            self.moneytype_popup.destroy()

        popup = tk.Toplevel(self.project)
        self.moneytype_popup = popup
        popup.configure(bg="#1e1e1e")
        popup.overrideredirect(True)
        popup.grab_set()

        w, h = 405, 180
        self.project.popup_offset_x = 10
        self.project.popup_offset_y = self.project.winfo_height() - h - 40
        popup.geometry(f"{w}x{h}+{self.project.winfo_x() + self.project.popup_offset_x}"
                       f"+{self.project.winfo_y() + self.project.popup_offset_y}")

        top_bar = tk.Frame(popup, bg="#5d5d5d")
        top_bar.pack(fill="x")
        tk.Button(
            top_bar, text="x", fg="white", bg="#5d5d5d",
            relief="flat", bd=0, font=("Arial", 14), command=popup.destroy
        ).pack(side="right", padx=8)

        items = [("💵", "Cash"), ("🏦", "Account"), ("💳", "Card")]
        body = tk.Frame(popup, bg="#1e1e1e")
        body.pack(pady=20)

        def choose(icon, text):
            target_var.set(f"{icon} {text}")
            popup.destroy()

        for i, (icon, name) in enumerate(items):
            tk.Button(
                body, text=f"{icon}  {name}", fg="white", bg="#333333",
                font=("Arial", 12), width=12, relief="flat",
                command=lambda ic=icon, nm=name: choose(ic, nm)
            ).grid(row=0, column=i, padx=5)

    def open_set_goal_popup(self):
        popup = tk.Toplevel(self.project)
        popup.configure(bg="#2b2b2b")
        popup.overrideredirect(True)
        popup.resizable(False, False)
        popup.grab_set()

        w, h = 280, 220
        x = self.project.winfo_x() + (self.project.winfo_width() - w) // 2
        y = self.project.winfo_y() + (self.project.winfo_height() - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(popup, text="Set Monthly Goal", fg="white", bg="#2b2b2b",
                 font=("Arial", 14, "bold")).pack(pady=20)

        entry_frame = tk.Frame(popup, bg="#333333", padx=10, pady=5)
        entry_frame.pack(fill="x", padx=30)

        tk.Label(entry_frame, text="RM", fg="#888888", bg="#333333",
                 font=("Arial", 12)).pack(side="left")

        goal_var = tk.StringVar(value=str(float(self.project.monthly_goal)))
        entry = tk.Entry(entry_frame, textvariable=goal_var, bg="#333333", fg="white",
                         font=("Arial", 14), bd=0, width=10, insertbackground="white")
        entry.pack(side="left", padx=5)
        entry.focus_set()

        def save_goal():
            try:
                val = float(goal_var.get())
                if val < 0:
                    raise ValueError
                self.project.monthly_goal = val
                self.project.tabs_manager.update_budget_page()
                popup.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive number.")

        btn_frame = tk.Frame(popup, bg="#2b2b2b")
        btn_frame.pack(fill="x", side="bottom", pady=20)

        tk.Button(btn_frame, text="Cancel", fg="#ff5555", bg="#2b2b2b", bd=0,
                  font=("Arial", 11), command=popup.destroy).pack(side="left", expand=True)

        tk.Button(btn_frame, text="Save Goal", fg="#4caf50", bg="#2b2b2b", bd=0,
                  font=("Arial", 11, "bold"), command=save_goal).pack(side="right", expand=True)


    # ---------------- Window Following (Binding) ----------------
    def center_popup(self, popup, w, h):
        popup.update_idletasks()

        main_x = self.project.winfo_x()
        main_y = self.project.winfo_y()
        main_w = self.project.winfo_width()
        main_h = self.project.winfo_height()

        x = main_x + (main_w - w) // 2
        y = main_y + (main_h - h) // 2

        popup.geometry(f"{w}x{h}+{x}+{y}")

    def update_popup_position(self, event=None):
        """Repositions Toplevel popups when the main window moves."""
        if event and event.widget != self.project:
            return

        main_x = self.project.winfo_x()
        main_y = self.project.winfo_y()
        main_width = self.project.winfo_width()
        main_height = self.project.winfo_height()

        # Reposition Date Popup (Calendar)
        if hasattr(self, "dt_popup") and self.dt_popup.winfo_exists():
            w, h = 300, 420
            popup_x = main_x + (main_width - w) // 2
            popup_y = main_y + (main_height - h) // 2
            self.dt_popup.geometry(f"{w}x{h}+{popup_x}+{popup_y}")

        # Reposition Time Popup
        if hasattr(self, "time_popup") and self.time_popup.winfo_exists():
            w, h = 220, 150
            popup_x = main_x + (main_width - w) // 2
            popup_y = main_y + (main_height - h) // 2
            self.time_popup.geometry(f"{w}x{h}+{popup_x}+{popup_y}")

        # Reposition Category Popup
        if hasattr(self, "category_popup") and self.category_popup.winfo_exists():
            w, h = 406, 290
            popup_x = main_x + self.project.popup_offset_x
            popup_y = main_y + self.project.popup_offset_y
            self.category_popup.geometry(f"{w}x{h}+{popup_x}+{popup_y}")

        # Reposition Money Type Popup
        if hasattr(self, "moneytype_popup") and self.moneytype_popup.winfo_exists():
            w, h = 405, 180
            popup_x = main_x + self.project.popup_offset_x
            popup_y = main_y + self.project.popup_offset_y
            self.moneytype_popup.geometry(f"{w}x{h}+{popup_x}+{popup_y}")

    # ---------------- Transaction Saving Logic ----------------

    def save_transaction(self):
        try:
            # Check for empty string before conversion
            amount_str = self.amount_var.get().strip()
            if not amount_str:
                raise ValueError("Amount cannot be empty.")

            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Amount must be a positive number. ({e})")
            return

        transaction_type = self.project.current_add_type
        note_content = self.note_input.get() if hasattr(self, 'note_input') else ""

        transaction = {
            'type': transaction_type,
            'amount': amount,
            'date': self.project.selected_datetime,
            'note': note_content
        }

        if transaction_type == "Transfer":
            if not self.category_var.get() or not self.money_type_var.get():
                messagebox.showerror("Invalid Input", "Select 'From' and 'To' accounts for Transfer.")
                return

            transaction['account_from'] = self.category_var.get()
            transaction['account_to'] = self.money_type_var.get()

        else:
            if not self.category_var.get() or not self.money_type_var.get():
                messagebox.showerror("Invalid Input", "Select 'Category' and 'Money Types'.")
                return

            transaction['category'] = self.category_var.get()
            transaction['account'] = self.money_type_var.get()

        self.project.transactions.append(transaction)

        if transaction_type == "Income":
            self.project.data.add_income(amount)
        elif transaction_type == "Expenses":
            self.project.data.add_expense(amount)

        self.project.update_stats()
        self.project.tabs_manager.update_daily_page()
        self.project.save_data()
        self.close_add_page()