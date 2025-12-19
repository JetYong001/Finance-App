import tkinter as tk
from PIL import Image, ImageTk
import random  # Used to generate random heights for the chart
import pygame

# ================= Configuration =================
SPLASH_BG_COLOR = "#222831"  # Dark background (Professional)
TEXT_COLOR = "#ffffff"  # White text
CHART_COLOR = "#00adb5"  # Cyan/Teal color for the chart bars
IMAGE_PATH = "images/logo.png"  # Path to your logo
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 700  # Taller to fit the chart
IMAGE_SIZE = (150, 150)  # Logo size
ANIMATION_SPEED = 30  # Milliseconds between frames (lower = smoother)


# ===============================================

class SplashApp(tk.Tk):
    def __init__(self, on_complete_callback):
        """
        :param on_complete_callback: The function to run when animation ends.
        """
        pygame.mixer.init()
        self.money_come_sound()
        super().__init__()
        self.on_complete_callback = on_complete_callback

        # 1. Window Setup (Borderless)
        self.overrideredirect(True)
        self.config(bg=SPLASH_BG_COLOR)
        self._center_window()

        # 2. UI Layout (Logo & Text)
        self._setup_ui()

        # 3. Animation Setup
        self.canvas_width = 250
        self.canvas_height = 200
        self.bars = []  # List to store rectangle objects
        self.bar_target_heights = []  # The final height each bar should reach
        self.bar_curr_heights = []  # The current height during animation

        # Initialize the chart canvas
        self._init_chart()

        # 4. Start the animation loop
        self.animation_step = 0
        self.after(100, self._animate_loop)

    def _center_window(self):
        """Calculates screen center and positions window."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def _setup_ui(self):
        """Loads the image safely and adds text labels."""
        # --- Image Loading ---
        try:
            # 1. Open Image (PIL Object)
            pil_image = Image.open(IMAGE_PATH)

            # 2. Resize Logic (Auto-compatibility for PIL versions)
            try:
                resample_method = Image.Resampling.LANCZOS  # New Pillow
            except AttributeError:
                resample_method = Image.LANCZOS  # Old Pillow

            pil_image = pil_image.resize(IMAGE_SIZE, resample_method)

            # 3. Convert to Tkinter Object
            self.tk_image = ImageTk.PhotoImage(pil_image)

            # 4. Display Image
            tk.Label(self, image=self.tk_image, bg=SPLASH_BG_COLOR, bd=0).pack(pady=(110, 10))

        except Exception as e:
            print(f"Image Error: {e}")
            tk.Label(self, text="$$$", font=("Arial", 40), bg=SPLASH_BG_COLOR, fg=CHART_COLOR).pack(pady=30)

        # --- Text Labels ---
        tk.Label(self, text="Finance Tracker", font=("Helvetica", 18, "bold"),
                 bg=SPLASH_BG_COLOR, fg=TEXT_COLOR).pack()

        self.loading_label = tk.Label(self, text="Analyzing market data...", font=("Arial", 9),
                                      bg=SPLASH_BG_COLOR, fg="#7f8c8d")
        self.loading_label.pack(side=tk.BOTTOM, pady=15)

    def _init_chart(self):
        """Creates the Canvas and the initial flat bars."""
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height,
                                bg=SPLASH_BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=20)


        # Create 5 bars
        num_bars = 6
        bar_width = 25
        gap = 15
        total_width = (num_bars * bar_width) + ((num_bars - 1) * gap)
        start_x = (self.canvas_width - total_width) // 2

        for i in range(num_bars):
            # Calculate X positions
            x1 = start_x + i * (bar_width + gap)
            x2 = x1 + bar_width

            # Start at the bottom (y = canvas_height)
            rect = self.canvas.create_rectangle(x1, self.canvas_height, x2, self.canvas_height,
                                                fill=CHART_COLOR, outline="")
            self.bars.append(rect)
            self.bar_curr_heights.append(0)

            # Random target height (between 30% and 90% of canvas height)
            target = random.uniform(0.3, 0.9) * self.canvas_height
            self.bar_target_heights.append(target)

    def _animate_loop(self):
        """Update bar heights to create a growing effect."""

        all_finished = True

        for i in range(len(self.bars)):
            current_h = self.bar_curr_heights[i]
            target_h = self.bar_target_heights[i]

            # If bar hasn't reached target yet
            if current_h < target_h:
                all_finished = False
                # Easing logic: Move 10% of the remaining distance (Smooth deceleration)
                growth = (target_h - current_h) * 0.1
                if growth < 0.5: growth = 0.5  # Minimum speed

                self.bar_curr_heights[i] += growth

                # Update Canvas Coordinates
                # Y axis is inverted in Canvas (0 is top, height is bottom)
                new_y = self.canvas_height - self.bar_curr_heights[i]
                coords = self.canvas.coords(self.bars[i])
                # coords = [x1, y1, x2, y2] -> Update y1
                self.canvas.coords(self.bars[i], coords[0], new_y, coords[2], self.canvas_height)

        # Update text dots animation
        self.animation_step += 1
        dots = "." * ((self.animation_step // 5) % 4)
        self.loading_label.config(text=f"Syncing secure data{dots}")


        if all_finished or self.animation_step > 150:
            self.after(500, self.finish)  # Wait 0.5s then finish
        else:
            self.after(ANIMATION_SPEED, self._animate_loop)  # Run next frame

    def finish(self):
        """Destroy splash and run main app."""
        self.destroy()
        self.on_complete_callback()

    def money_come_sound(self):
        try:
            pygame.mixer.music.load("sound_effect/moneycome.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error: {e}")