import tkinter as tk
import json
import os
import pygame


class LoginManager:
    def __init__(self, app,add_trans):
        """
        Initialize the login manager.
        :param app: Instance of the main program FinanceApp (self)
        """
        self.app = app
        self.add_trans = add_trans

        # Define necessary Frames inside the manager or attach directly to the app
        self.login_frame = tk.Frame(self.app, bg="#1e1e1e")
        self.register_frame = tk.Frame(self.app, bg="#1e1e1e")
        self.forgot_frame = tk.Frame(self.app, bg="#1e1e1e")

        # Reference the user_file path from the main program
        self.user_file = self.app.user_file

        # Build UI and show the login page
        self.build_login_ui()
        self.show_login()

    # ---------------- Login / Register UI ----------------
    def build_login_ui(self):
        # 1. Login Frame
        tk.Label(self.login_frame, text="Finance Tracker", bg="#1e1e1e", fg="white",
                 font=("Arial", 24, "bold")).pack(pady=(80, 40))

        tk.Label(self.login_frame, text="Username", bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w", padx=40)

        self.login_user_frame = tk.Frame(self.login_frame, bg="#444444")
        self.login_user_frame.pack(pady=(0, 10), padx=40, fill="x")

        self.entry_user = tk.Entry(self.login_frame, font=("Arial", 12), bg="#333333", fg="white", bd=0)
        self.entry_user.pack(fill="x", padx=40, pady=(0, 20), ipady=9)

        tk.Label(self.login_frame, text="Password", bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w", padx=40)

        self.login_pass_frame = tk.Frame(self.login_frame, bg="#444444")
        self.login_pass_frame.pack(pady=(0, 20), padx=40, fill="x")

        self.entry_pass = tk.Entry(self.login_frame, font=("Arial", 13), bg="#333333", fg="white", bd=0, show="*")
        self.entry_pass.pack(fill="x", padx=40, pady=(0, 30), ipady=8)

        tk.Button(self.login_frame, text="Login", bg="#2a9df4", fg="white", font=("Arial", 12, "bold"), bd=0,
                  command=self.perform_login).pack(fill="x", padx=40, ipady=10)

        self.login_message = tk.Label(self.login_frame, text="", fg="white", bg="#1e1e1e", font=("Arial", 10))
        self.login_message.pack()

        # Actions Frame (Create Account / Forgot Password)
        actions_frame = tk.Frame(self.login_frame, bg="#1e1e1e")
        actions_frame.pack(pady=20)

        tk.Button(actions_frame, text="Create Account", bg="#1e1e1e", fg="#2a9df4", bd=0,
                  font=("Arial", 10, "bold"), cursor="hand2",
                  command=self.show_register).pack(side="left", padx=15)

        tk.Label(actions_frame, text="|", bg="#1e1e1e", fg="#555").pack(side="left")

        tk.Button(actions_frame, text="Forgot Password?", bg="#1e1e1e", fg="#ff5555", bd=0,
                  font=("Arial", 10, "bold"), cursor="hand2",
                  command=self.show_forgot_password).pack(side="left", padx=15)

        # 2. Register Frame
        tk.Label(self.register_frame, text="Create Account", bg="#1e1e1e", fg="white",
                 font=("Arial", 24, "bold")).pack(pady=(80, 40))

        tk.Label(self.register_frame, text="New Username", bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w", padx=40)

        self.reg_user_frame = tk.Frame(self.register_frame, bg="#444444")
        self.reg_user_frame.pack(pady=(0, 10), padx=40, fill="x")

        self.reg_user = tk.Entry(self.register_frame, font=("Arial", 12), bg="#333333", fg="white", bd=0)
        self.reg_user.pack(fill="x", padx=40, pady=(0, 20), ipady=8)

        tk.Label(self.register_frame, text="New Password", bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w", padx=40)

        self.reg_pass_frame = tk.Frame(self.register_frame, bg="#444444")
        self.reg_pass_frame.pack(pady=(0, 20), padx=40, fill="x")

        self.reg_pass = tk.Entry(self.register_frame, font=("Arial", 12), bg="#333333", fg="white", bd=0, show="*")
        self.reg_pass.pack(fill="x", padx=40, pady=(0, 30), ipady=8)

        tk.Button(self.register_frame, text="Sign Up", bg="#ff5555", fg="white", font=("Arial", 12, "bold"), bd=0,
                  command=self.perform_register).pack(fill="x", padx=40, ipady=10)

        tk.Button(self.register_frame, text="Back to Login", bg="#1e1e1e", fg="#aaaaaa", bd=0,
                  command=self.show_login).pack(pady=20)

        self.register_message = tk.Label(self.register_frame, text="", fg="white", bg="#1e1e1e", font=("Arial", 10))
        self.register_message.pack()

        # 3. Forgot Frame
        tk.Label(self.forgot_frame, text="Reset Password", bg="#1e1e1e", fg="white",
                 font=("Arial", 24, "bold")).pack(pady=(80, 40))

        tk.Label(self.forgot_frame, text="Username", bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w", padx=40)
        self.forgot_user = tk.Entry(self.forgot_frame, font=("Arial", 12), bg="#333333", fg="white", bd=0)
        self.forgot_user.pack(fill="x", padx=40, pady=(0, 20), ipady=8)

        tk.Label(self.forgot_frame, text="New Password", bg="#1e1e1e", fg="#aaaaaa").pack(anchor="w", padx=40)
        self.forgot_pass = tk.Entry(self.forgot_frame, font=("Arial", 12), bg="#333333", fg="white", bd=0, show="*")
        self.forgot_pass.pack(fill="x", padx=40, pady=(0, 30), ipady=8)

        tk.Button(self.forgot_frame, text="Update Password", bg="#ffa500", fg="black", font=("Arial", 12, "bold"), bd=0,
                  command=self.perform_reset).pack(fill="x", padx=40, ipady=10)

        tk.Button(self.forgot_frame, text="Back to Login", bg="#1e1e1e", fg="#aaaaaa", bd=0,
                  command=self.show_login).pack(pady=20)

        self.reset_msg = tk.Label(self.forgot_frame, text="", bg="#1e1e1e", fg="red", font=("Arial", 10))
        self.reset_msg.pack(pady=5)

    def show_login(self):
        self.register_frame.pack_forget()
        self.forgot_frame.pack_forget()
        self.login_message.config(text="", fg="white")
        self.login_frame.pack(fill="both", expand=True)

    def show_register(self):
        self.login_frame.pack_forget()
        self.forgot_frame.pack_forget()
        self.register_message.config(text="", fg="white")
        self.register_frame.pack(fill="both", expand=True)

    def show_forgot_password(self):
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.reset_msg.config(text="")

        if hasattr(self, 'forgot_user'): self.forgot_user.delete(0, 'end')
        if hasattr(self, 'forgot_pass'): self.forgot_pass.delete(0, 'end')
        self.forgot_frame.pack(fill="both", expand=True)

    def perform_reset(self):
        u = self.forgot_user.get().strip()
        new_p = self.forgot_pass.get().strip()

        self.reset_msg.config(text="", fg="red")

        if not u or not new_p:
            self.reset_msg.config(text="Please fill all fields")
            return

        if not os.path.exists(self.user_file):
            self.reset_msg.config(text="No users found.")
            return

        with open(self.user_file, 'r') as f:
            users = json.load(f)

        if u in users:
            users[u] = new_p
            with open(self.user_file, 'w') as f:
                json.dump(users, f)

            self.reset_msg.config(text="Password reset successfully!", fg="green")
            self.app.after(1500, self.show_login)
        else:
            self.reset_msg.config(text="Username not found.")

    def perform_login(self):
        u = self.entry_user.get().strip()
        p = self.entry_pass.get().strip()

        self.login_user_frame.config(bg="#444444")
        self.login_pass_frame.config(bg="#444444")
        self.login_message.config(text="")

        if not os.path.exists(self.app.user_file):
            with open(self.user_file, 'w') as f:
                json.dump({}, f)


        with open(self.app.user_file, 'r') as f:
            users = json.load(f)

        if u not in users:
            self.not_register_sound()
            self.login_message.config(text="⚠ No users found.", fg="red")
            self.login_user_frame.config(bg="red")
            self.login_pass_frame.config(bg="red")
            return

        if u not in users or users[u] != p:
            self.login_message.config(text="❌ Invalid username or password", fg="red")
            self.login_user_frame.config(bg="red")
            self.login_pass_frame.config(bg="red")
            return

        # Login successful, set current_user in main app
        self.app.current_user = u

        self.login_message.config(text="✔ Login successful!", fg="lightgreen")

        # Delay then enter main interface
        self.app.after(400, lambda: [
            self.sound(),
            self.login_frame.pack_forget(),
            self.app.load_data(),  # Call main app's load data
            self.app.build_ui()  # Call main app's build UI
        ])

    def perform_register(self):
        u = self.reg_user.get().strip()
        p = self.reg_pass.get().strip()

        self.reg_user_frame.config(bg="#444444")
        self.reg_pass_frame.config(bg="#444444")
        self.register_message.config(text="")

        if not u or not p:
            self.register_message.config(text="⚠ All fields required.", fg="red")
            self.reg_user_frame.config(bg="red")
            self.reg_pass_frame.config(bg="red")
            return

        if os.path.exists(self.user_file):
            with open(self.user_file, "r") as f:
                users = json.load(f)
        else:
            users = {}

        if u in users:
            self.register_message.config(text="⚠ Username already exists.", fg="red")
            self.reg_user_frame.config(bg="red")
            return

        users[u] = p
        with open(self.user_file, "w") as f:
            json.dump(users, f, indent=4)

        self.dadada_sound()
        self.register_message.config(text="✔ Account created!", fg="lightgreen")
        self.app.after(600, self.show_login)

    def logout(self):
        self.app.current_user = None

        # Clear login feedback message
        self.login_message.config(text="", fg="white")

        # Hide all main app UI
        try:
            if hasattr(self.app, 'top_section'): self.app.top_section.pack_forget()
            if hasattr(self.app, 'tabs_section'): self.app.tabs_section.pack_forget()
            if hasattr(self.app, 'stats_section'): self.app.stats_section.pack_forget()

            # Hide all pages
            if hasattr(self.app, 'pages'):
                for p in self.app.pages:
                    p.pack_forget()

            # Hide all bottom pages
            if hasattr(self.app, 'bottom_pages'):
                for frame in self.app.bottom_pages.values():
                    frame.pack_forget()

            # Hide bottom navigation bar
            if hasattr(self.app, 'bottom_frame'):
                self.app.bottom_frame.pack_forget()
        except:
            pass

        # Hide add button
        try:
            self.app.add_btn.place_forget()
        except:
            pass

        # Reset main program data
        self.app.bottom_pages = {}
        self.app.transactions = []
        if hasattr(self.app, 'data'):
            self.app.data.clear()

        # Clear login input fields
        self.entry_user.delete(0, "end")
        self.entry_pass.delete(0, "end")

        # Return to login screen
        self.show_login()

    def sound(self):
        try:
            pygame.mixer.music.load("sound_effect/gay.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error: {e}")

    def not_register_sound(self):
        try:
            pygame.mixer.music.load("sound_effect/not_register_yet.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error: {e}")

    def dadada_sound(self):
        try:
            pygame.mixer.music.load("sound_effect/dadada.mpeg")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error: {e}")