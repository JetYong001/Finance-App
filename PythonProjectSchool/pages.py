import tkinter as tk
import json
from tkinter import messagebox,filedialog
import os
from PIL import Image, ImageTk, ImageDraw, ImageOps
import pygame

from utlis import extract_icon




class PagesManager:
    def __init__(self, project):
        self.project = project
        self.avatar_filename = "user_avatars.json"

        # Check if the JSON file exists to avoid errors
        if os.path.exists(self.avatar_filename):
            try:
                # Open the JSON file in read mode
                with open(self.avatar_filename, "r") as f:
                    # Load the dictionary: {"username": "path/to/image"}
                    self.project.user_avatars = json.load(f)
            except Exception as e:
                print(f"Error loading JSON: {e}")
                # If error occurs, start with an empty dictionary
                self.project.user_avatars = {}
        else:
            # If file doesn't exist yet, create an empty dictionary
            self.project.user_avatars = {}

        self.change_pass_visible = False
        self.tk_avatar_img = None

    # ===================TAX CALCULATION=============================
    def update_calcTax_page(self):
        if "Tax Calc." not in self.project.bottom_pages:
            self.project.bottom_pages["Tax Calc."] = tk.Frame(self.project, bg="#1e1e1e")

        tax_calc_frame = self.project.bottom_pages["Tax Calc."]

        for widget in tax_calc_frame.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(tax_calc_frame, bg="#1e1e1e", padx=15, pady=20)
        main_frame.pack(fill="both", expand=True, anchor="n")

        # Title
        tk.Label(main_frame, text="🇲🇾 Tax Calculator", bg="#1e1e1e", fg="white",
                 font=("Arial", 14, "bold")).pack(pady=(0, 20), anchor="w")

        # --- 1. Choose calculate mode ---
        tk.Label(main_frame, text="Calculate Mode:", bg="#1e1e1e", fg="#aaaaaa",
                 font=("Arial", 10)).pack(pady=(10, 5), anchor="w")

        mode_frame = tk.Frame(main_frame, bg="#1e1e1e")
        mode_frame.pack(fill="x", pady=(0, 15))

        tk.Radiobutton(mode_frame, text="Monthly", variable=self.project.tax_calc_mode_var, value="Monthly",
                       bg="#1e1e1e", fg="white", selectcolor="#1e1e1e",
                       activebackground="#1e1e1e", font=("Arial", 11)).pack(side="left", padx=10)

        tk.Radiobutton(mode_frame, text="Yearly", variable=self.project.tax_calc_mode_var, value="Yearly",
                       bg="#1e1e1e", fg="white", selectcolor="#1e1e1e",
                       activebackground="#1e1e1e", font=("Arial", 11)).pack(side="left", padx=10)

        # --- 2. input income ---
        tk.Label(main_frame, text="Enter your income amount (RM):", bg="#1e1e1e", fg="#aaaaaa",
                 font=("Arial", 10)).pack(pady=(10, 5), anchor="w")

        tk.Entry(main_frame, textvariable=self.project.tax_income_var, font=("Arial", 12),
                 bg="#333333", fg="white", bd=0, insertbackground="white",
                 justify="left", relief="flat").pack(fill="x", ipady=8)

        # --- 3. calculate tax  ---
        tk.Button(main_frame, text="Calculate tax", bg="#2a9df4", fg="white", font=("Arial", 12, "bold"), bd=0,
                  command=self.calculate_tax_from_ui, relief="flat").pack(fill="x", ipady=10, pady=20)

        # --- 4. show result ---
        result_label_frame = tk.Frame(main_frame, bg="#2b2b2b", padx=15, pady=15, relief="flat", bd=1)
        result_label_frame.pack(fill="x", pady=(10, 0))

        tk.Label(result_label_frame, text="Result:", bg="#2b2b2b", fg="white",
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))

        tk.Label(result_label_frame, textvariable=self.project.tax_result_var, bg="#2b2b2b", fg="#cfcfcf",
                 font=("Arial", 12), justify=tk.LEFT).pack(anchor="w")

    def calculate_tax_from_ui(self):
        try:
            income_str = self.project.tax_income_var.get().strip().replace(',', '')
            if not income_str:
                messagebox.showerror("Error", "Please enter your income in positif number!")
                return

            income = float(income_str)
            mode = self.project.tax_calc_mode_var.get()

            # 1. change calculate mode
            if mode == "Monthly":
                gross_annual_income = income * 12
            elif mode == "Yearly":
                gross_annual_income = income
            else:
                return  # Should not happen

            # 2. Chargeable Income
            chargeable_income = self._get_chargeable_income(gross_annual_income)

            # 3. Calculate tax payable
            tax_payable = self.calculate_malaysia_tax_logic(chargeable_income)

            # 4. show result
            result_text = (
                f"Calcutale Mode: {mode} \n"
                f"Gross Annual Income: RM {gross_annual_income:,.2f} \n"
                f"Individual Relief: RM 9,000.00 \n"
                f"Chargeable Income: RM {chargeable_income:,.2f} \n"
                f"Tax Payable: RM {tax_payable:,.2f}"
            )
            self.project.tax_result_var.set(result_text)

        except ValueError:
            messagebox.showerror("Error", "Please enter a positif number!")
        except Exception as e:
            messagebox.showerror("Error", f"Error occurs!: {e}")

    def _get_chargeable_income(self, gross_annual_income: float) -> float:
        INDIVIDUAL_RELIEF = 9000.0
        return max(0.0, gross_annual_income - INDIVIDUAL_RELIEF)

    def calculate_malaysia_tax_logic(self, chargeable_income: float) -> float:

        # struc: (upper limit,cumulative amount , over tax rate)
        TAX_BRACKETS = [
            (5000, 0.0, 0.0),
            (20000, 0.0, 0.01),
            (35000, 150.0, 0.03),
            (50000, 600.0, 0.06),
            (70000, 1500.0, 0.11),
            (100000, 3700.0, 0.19),
            (400000, 9400.0, 0.25),
            (600000, 84400.0, 0.26),
            (2000000, 136400.0, 0.28),
            (float('inf'), 528400.0, 0.30)
        ]

        tax_payable = 0.0
        previous_threshold = 0.0

        if chargeable_income <= 0:
            return 0.0

        for threshold, cumulative_tax_before_band, rate in TAX_BRACKETS:
            if chargeable_income <= threshold:
                taxable_in_this_band = chargeable_income - previous_threshold

                if threshold == 5000:
                    tax_payable = 0.0
                elif threshold == 20000:
                    tax_payable = (chargeable_income - 5000) * rate
                else:
                    tax_payable = cumulative_tax_before_band + (taxable_in_this_band * rate)
                break

            previous_threshold = threshold

        # Tax Rebate - RM400, for those chargeable income no more than RM35,000
        if 0 < chargeable_income <= 35000:
            tax_payable -= 400.0

        return max(0.0, tax_payable)

    # ==================== STATS PAGE (No Canvas, JSON Data) ====================

    def update_stats_page(self):

        if "Stats" not in self.project.bottom_pages:
            self.project.bottom_pages["Stats"] = tk.Frame(self.project, bg="#1e1e1e")

        page = self.project.bottom_pages["Stats"]

        for widget in page.winfo_children():
            widget.destroy()

        target_month = self.project.current_date.month
        target_year = self.project.current_date.year

        monthly_trans = [
            t for t in self.project.transactions
            if t['date'].month == target_month and t['date'].year == target_year
        ]

        total_income = sum(t['amount'] for t in monthly_trans if t['type'] == "Income")
        total_expense = sum(t['amount'] for t in monthly_trans if t['type'] == "Expenses")

        tabs_frame = tk.Frame(page, bg="#1e1e1e")
        tabs_frame.pack(fill="x", pady=(10, 0))
        tabs_frame.columnconfigure(0, weight=1)
        tabs_frame.columnconfigure(1, weight=1)

        active_fg = "white"
        inactive_fg = "#666666"
        accent_color = "#ff5555"

        # Income button
        inc_fg = active_fg if self.project.stats_view_mode == "Income" else inactive_fg
        tk.Button(tabs_frame, text="Income", bg="#1e1e1e", fg=inc_fg,
                  font=("Arial", 10, "bold"), bd=0, activebackground="#1e1e1e", activeforeground="white",
                  command=lambda: self.switch_stats_mode("Income")
                  ).grid(row=0, column=0, sticky="ew", pady=5)

        # Expenses button
        exp_fg = active_fg if self.project.stats_view_mode == "Expenses" else inactive_fg
        tk.Button(tabs_frame, text="Expenses", bg="#1e1e1e", fg=exp_fg,
                  font=("Arial", 10, "bold"), bd=0, activebackground="#1e1e1e", activeforeground="white",
                  command=lambda: self.switch_stats_mode("Expenses")
                  ).grid(row=0, column=1, sticky="ew", pady=5)

        # Indicator Line
        line_frame = tk.Frame(tabs_frame, bg="#333333", height=2)
        line_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        active_line = tk.Frame(tabs_frame, bg=accent_color, height=2)
        col_idx = 0 if self.project.stats_view_mode == "Income" else 1
        active_line.grid(row=1, column=col_idx, sticky="ew")

        # ---------------------------------------------------------
        # 4. View Mode
        # ---------------------------------------------------------
        current_data_list = []
        current_view_total = 0


        if self.project.stats_view_mode == "Income":
            for t in monthly_trans:
                if t['type'] == "Income": current_data_list.append(t)
            current_view_total = total_income
        else:
            for t in monthly_trans:
                if t['type'] == "Expenses": current_data_list.append(t)
            current_view_total = total_expense

        # ---------------------------------------------------------
        # 5. Total Display
        # ---------------------------------------------------------
        top_area = tk.Frame(page, bg="#1e1e1e", pady=15)
        top_area.pack(fill="x")

        if current_view_total == 0:
            tk.Label(top_area, text="No data available", fg="#666666", bg="#1e1e1e",
                     font=("Arial", 12)).pack()
        else:
            tk.Label(top_area, text="Total", fg="#888888", bg="#1e1e1e", font=("Arial", 10)).pack()

            tk.Label(top_area, text=f"RM {current_view_total:,.2f}", fg="white", bg="#1e1e1e",
                     font=("Arial", 24, "bold")).pack()

        tk.Frame(page, bg="#2b2b2b", height=1).pack(fill="x")

        # ---------------------------------------------------------
        # 6. List Area
        # ---------------------------------------------------------
        list_area = tk.Frame(page, bg="#1e1e1e")
        list_area.pack(fill="both", expand=True, padx=20, pady=10)

        if current_view_total > 0:

            cat_map = {}
            for t in current_data_list:
                if self.project.stats_view_mode == "Expenses":
                    key = t.get('category', 'Other')
                else:
                    key = t.get('category', 'Salary')
                cat_map[key] = cat_map.get(key, 0) + t['amount']

            sorted_cats = sorted(cat_map.items(), key=lambda x: x[1], reverse=True)

            for cat_name, amount in sorted_cats:
                percent = (amount / current_view_total) * 100
                self._build_category_row(list_area, cat_name, amount, percent)

    def _build_category_row(self, parent, cat_name, amount, percent):
        """Creates a single row in the stats list without Canvas."""
        row = tk.Frame(parent, bg="#1e1e1e", pady=8)
        row.pack(fill="x")

        # Icon Extraction
        icon = extract_icon(cat_name)
        if not icon: icon = "⚪"
        clean_name = cat_name.split(' ', 1)[-1] if ' ' in cat_name else cat_name

        # Icon Label
        tk.Label(row, text=icon, bg="#1e1e1e", fg="white", font=("Arial", 12)).pack(side="left", padx=(0, 10))

        # Middle Section (Name + Bar)
        mid_frame = tk.Frame(row, bg="#1e1e1e")
        mid_frame.pack(side="left", fill="x", expand=True)

        # Info Line (Name .... Percentage)
        info_frame = tk.Frame(mid_frame, bg="#1e1e1e")
        info_frame.pack(fill="x")
        tk.Label(info_frame, text=clean_name, bg="#1e1e1e", fg="white",
                 font=("Arial", 10, "bold")).pack(side="left")
        tk.Label(info_frame, text=f"{percent:.1f}%", bg="#1e1e1e", fg="#888888",
                 font=("Arial", 9)).pack(side="right")

        # Progress Bar (Using Frame)
        bar_bg = tk.Frame(mid_frame, bg="#333333", height=4)
        bar_bg.pack(fill="x", pady=(4, 0))

        # White bar for progress
        bar_fill = tk.Frame(bar_bg, bg="white", height=4)
        # Use place to handle percentage width relative to parent
        bar_fill.place(relx=0, rely=0, relheight=1, relwidth=min(percent / 100, 1.0))

        # Amount Label (Right side)
        tk.Label(row, text=f"{amount:,.0f}", bg="#1e1e1e", fg="white",
                 font=("Arial", 10)).pack(side="right", padx=(10, 0))

        # --- Helper Methods ---

    def switch_stats_mode(self, mode):
        if self.project.stats_view_mode != mode:
            self.project.stats_view_mode = mode
            self.update_stats_page()

    # ----------------------account page-----------------------------
    def update_account_page(self):
        """
        Renders the profile page.
        """
        # --- Container Setup ---
        if "Account" not in self.project.bottom_pages:
            self.project.bottom_pages["Account"] = tk.Frame(self.project, bg="#121212")

        page = self.project.bottom_pages["Account"]

        for widget in page.winfo_children():
            widget.destroy()

        # --- Header ---
        header = tk.Frame(page, bg="#121212")
        header.pack(fill="x", pady=(20, 10), padx=20)
        tk.Label(header, text="Profile", bg="#121212", fg="white", font=("Arial", 22, "bold")).pack(anchor="w")

        # --- Profile Card ---
        profile_card = tk.Frame(page, bg="#1e1e1e", padx=20, pady=25)
        profile_card.pack(fill="x", padx=20, pady=10)

        # [AVATAR SECTION]
        avatar_size = 70
        avatar_container = tk.Frame(profile_card, bg="#1e1e1e", cursor="hand2")
        avatar_container.pack(side="left", padx=(0, 20))

        avatar_canvas = tk.Canvas(avatar_container, width=avatar_size, height=avatar_size,
                                  bg="#1e1e1e", highlightthickness=0)
        avatar_canvas.pack()

        avatar_container.bind("<Button-1>", self.choose_avatar_image)
        avatar_canvas.bind("<Button-1>", self.choose_avatar_image)

        # --- [CORE LOGIC]: Load Image ---
        custom_image_loaded = False
        current_user = self.project.current_user

        # 1. Try to get custom image path
        user_img_path = self.project.user_avatars.get(current_user)

        # 2. Try to load custom image
        if user_img_path and os.path.exists(user_img_path):
            self.tk_avatar_img = self.get_circular_avatar(user_img_path, avatar_size)
            if self.tk_avatar_img:
                custom_image_loaded = True

        # --- [FALLBACK]: Use Generated Default Avatar ---
        # If no custom image found, generate the "Black Person in Circle"
        if not custom_image_loaded:
            self.tk_avatar_img = self.create_default_avatar(avatar_size)

        # 3. Draw the final image (Custom OR Default) onto the canvas
        # Since both are now processed images, we just use create_image
        if self.tk_avatar_img:
            avatar_canvas.create_image(avatar_size // 2, avatar_size // 2, image=self.tk_avatar_img)

        # --- User Details ---
        info_frame = tk.Frame(profile_card, bg="#1e1e1e")
        info_frame.pack(side="left", fill="both", expand=True)

        tk.Label(info_frame, text=current_user, fg="white", bg="#1e1e1e", font=("Arial", 16, "bold")).pack(anchor="w")
        tk.Label(info_frame, text="Tap avatar to change", fg="#888888", bg="#1e1e1e", font=("Arial", 10)).pack(
            anchor="w", pady=(5, 0))

        # --- Settings (Password) ---
        tk.Label(page, text="Security", fg="#888888", bg="#121212", font=("Arial", 10, "bold")).pack(anchor="w",
                                                                                                     padx=25,
                                                                                                     pady=(20, 5))

        settings_card = tk.Frame(page, bg="#1e1e1e")
        settings_card.pack(fill="x", padx=20)

        self.toggle_pass_btn = tk.Button(
            settings_card, text="🔒  Change Password", bg="#1e1e1e", fg="white", font=("Arial", 11), bd=0, relief="flat",
            activebackground="#333333", activeforeground="white", anchor="w", padx=20, pady=15,
            command=self.toggle_change_password
        )
        self.toggle_pass_btn.pack(fill="x")

        self.pass_divider = tk.Frame(settings_card, bg="#333333", height=1)
        self.change_pass_frame = tk.Frame(settings_card, bg="#252525", padx=20, pady=15)

        tk.Label(self.change_pass_frame, text="Enter New Password", fg="#aaaaaa", bg="#252525",
                 font=("Arial", 10)).pack(anchor="w")
        entry_bg = tk.Frame(self.change_pass_frame, bg="#333333", padx=10, pady=5)
        entry_bg.pack(fill="x", pady=5)
        self.account_new_pass = tk.Entry(entry_bg, show="•", bg="#333333", fg="white", bd=0, font=("Arial", 12),
                                         insertbackground="white")
        self.account_new_pass.pack(fill="x")
        self.account_msg = tk.Label(self.change_pass_frame, text="", fg="red", bg="#252525", font=("Arial", 9))
        self.account_msg.pack(anchor="w", pady=5)
        tk.Button(self.change_pass_frame, text="Update Password", bg="#2a9df4", fg="white", font=("Arial", 10, "bold"),
                  bd=0, relief="flat", pady=8, command=self.change_account_password).pack(fill="x")

        self.change_pass_visible = False
        self.change_pass_frame.pack_forget()

        tk.Frame(page, bg="#121212").pack(expand=True)
        logout_btn = tk.Button(page, text="Log Out", bg="#ff5555", fg="white", font=("Arial", 11, "bold"), bd=0,
                               relief="flat", pady=12, command=self.two_function)
        logout_btn.pack(fill="x", side="bottom", padx=20, pady=30)

    def create_default_avatar(self, size):
        bg_color = "#333333"
        silhouette_color = "#121212"
        img = Image.new("RGBA", (size, size), bg_color)
        draw = ImageDraw.Draw(img)

        head_radius = size * 0.2
        head_center_x = size / 2
        head_center_y = size * 0.35
        draw.ellipse((head_center_x - head_radius, head_center_y - head_radius,
                      head_center_x + head_radius, head_center_y + head_radius),
                     fill=silhouette_color)


        body_width = size * 0.8
        body_height = size * 0.6
        body_x0 = (size - body_width) / 2
        body_y0 = size * 0.65
        draw.ellipse((body_x0, body_y0, body_x0 + body_width, body_y0 + body_height),
                     fill=silhouette_color)


        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size, size), fill=255)

        img.putalpha(mask)

        return ImageTk.PhotoImage(img)

    def get_circular_avatar(self, image_path, size):
        """
        Loads an image from a path, resizes it, crops it into a circle,
        and returns a Tkinter-compatible PhotoImage.
        """
        try:
            # 1. Open the image and convert to RGBA (Red, Green, Blue, Alpha/Transparency)
            img = Image.open(image_path).convert("RGBA")

            # 2. Resize the image to fit the specific size (e.g., 70x70)
            #    LANCZOS filter ensures the image remains high quality when downscaled.
            #    centering=(0.5, 0.5) crops from the center.
            img = ImageOps.fit(img, (size, size), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

            # 3. Create a Mask for the circle
            #    - Create a new black image (L mode) of the same size.
            #    - Draw a solid white circle in the middle.
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)

            # 4. Apply the Mask
            #    - White areas of the mask keep the image opaque.
            #    - Black areas of the mask make the image transparent.
            img.putalpha(mask)

            # 5. Convert to Tkinter object
            tk_img = ImageTk.PhotoImage(img)
            return tk_img

        except Exception as e:
            print(f"Error processing avatar image: {e}")
            return None

    def choose_avatar_image(self, event=None):
        """
        Allows user to select image, updates dictionary, and SAVES to JSON.
        """
        file_path = filedialog.askopenfilename(
            title="Select Profile Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )

        if file_path:
            # 1. Update Memory
            current_user = self.project.current_user
            self.project.user_avatars[current_user] = file_path

            # 2. Save to JSON File (Persistent Storage)
            try:
                # Ensure you defined self.avatar_file in __init__
                # If not, replace self.avatar_file with "user_avatars.json"
                filename = getattr(self, "avatar_file", "user_avatars.json")

                with open(filename, "w") as f:
                    json.dump(self.project.user_avatars, f, indent=4)
                print(f"Avatar saved for {current_user}")
            except Exception as e:
                print(f"Error saving avatar JSON: {e}")

            # 3. Refresh UI
            self.update_account_page()

    def change_account_password(self):
        new_p = self.account_new_pass.get().strip()
        self.account_msg.config(text="", fg="red")

        if not new_p:
            self.account_msg.config(text="Password cannot be empty.")
            return

        if not os.path.exists(self.project.user_file):
            self.account_msg.config(text="User file not found.")
            return

        with open(self.project.user_file, "r") as f:
            users = json.load(f)

        users[self.project.current_user] = new_p

        with open(self.project.user_file, "w") as f:
            json.dump(users, f, indent=4)

        self.account_msg.config(text="Password updated successfully.", fg="lightgreen")
        self.account_new_pass.delete(0, "end")

    def toggle_change_password(self):
        if self.change_pass_visible:
            self.change_pass_frame.pack_forget()
            self.toggle_pass_btn.config(text="Change Password")
        else:
            self.change_pass_frame.pack(fill="x")
            self.toggle_pass_btn.config(text="Cancel")

        self.account_msg.config(text="", fg="white")

        self.change_pass_visible = not self.change_pass_visible

    def bye_bye_sound(self):
        try:
            pygame.mixer.music.load("sound_effect/byebye.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error: {e}")

    def two_function(self):
        self.bye_bye_sound()
        self.project.login_manager.logout()