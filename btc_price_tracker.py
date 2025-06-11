import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime
import threading
import time

class BitcoinPriceTracker:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("Bitcoin Price Tracker - Indodax")
        self.app.configure(bg='#0d1117')
        self.app.state('zoomed')

        self.current_price = 0
        self.previous_price = 0
        self.price_change = 0
        self.price_change_percent = 0
        self.last_update = ""
        self.is_running = True

        self.setup_ui()
        self.start_price_updates()

        self.app.bind('<Escape>', self.toggle_fullscreen)
        self.app.bind('<F11>', self.toggle_fullscreen)

    def setup_ui(self):
        main_frame = tk.Frame(self.app, bg='#0d1117')
        main_frame.pack(expand=True, fill='both')

        title_frame = tk.Frame(main_frame, bg='#0d1117')
        title_frame.pack(pady=(50, 30))

        title_label = tk.Label(
            title_frame,
            text="₿ BITCOIN PRICE TRACKER",
            font=('Segoe UI', 32, 'bold'),
            fg='#f39c12',
            bg='#0d1117'
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Live prices from Indodax",
            font=('Segoe UI', 14),
            fg='#8b949e',
            bg='#0d1117'
        )
        subtitle_label.pack(pady=(5, 0))

        price_frame = tk.Frame(main_frame, bg='#21262d', relief='raised', bd=2)
        price_frame.pack(pady=30, padx=100, fill='x')

        self.price_label = tk.Label(
            price_frame,
            text="Loading...",
            font=('Segoe UI', 48, 'bold'),
            fg='#58a6ff',
            bg='#21262d'
        )
        self.price_label.pack(pady=30)

        self.change_label = tk.Label(
            price_frame,
            text="",
            font=('Segoe UI', 18, 'bold'),
            bg='#21262d'
        )
        self.change_label.pack(pady=(0, 20))

        info_frame = tk.Frame(main_frame, bg='#0d1117')
        info_frame.pack(pady=30, fill='x')

        cards_frame = tk.Frame(info_frame, bg='#0d1117')
        cards_frame.pack()

        update_card = tk.Frame(cards_frame, bg='#161b22', relief='raised', bd=1)
        update_card.pack(side='left', padx=20, pady=10, ipadx=20, ipady=15)

        tk.Label(
            update_card,
            text="Last Update",
            font=('Segoe UI', 12, 'bold'),
            fg='#8b949e',
            bg='#161b22'
        ).pack()

        self.update_label = tk.Label(
            update_card,
            text="--:--:--",
            font=('Segoe UI', 14),
            fg='#f0f6fc',
            bg='#161b22'
        )
        self.update_label.pack(pady=(5, 0))

        status_card = tk.Frame(cards_frame, bg='#161b22', relief='raised', bd=1)
        status_card.pack(side='left', padx=20, pady=10, ipadx=20, ipady=15)

        tk.Label(
            status_card,
            text="Status",
            font=('Segoe UI', 12, 'bold'),
            fg='#8b949e',
            bg='#161b22'
        ).pack()

        self.status_label = tk.Label(
            status_card,
            text="●  Live",
            font=('Segoe UI', 14),
            fg='#3fb950',
            bg='#161b22'
        )
        self.status_label.pack(pady=(5, 0))

        exchange_card = tk.Frame(cards_frame, bg='#161b22', relief='raised', bd=1)
        exchange_card.pack(side='left', padx=20, pady=10, ipadx=20, ipady=15)

        tk.Label(
            exchange_card,
            text="Exchange",
            font=('Segoe UI', 12, 'bold'),
            fg='#8b949e',
            bg='#161b22'
        ).pack()

        tk.Label(
            exchange_card,
            text="Indodax",
            font=('Segoe UI', 14),
            fg='#f0f6fc',
            bg='#161b22'
        ).pack(pady=(5, 0))

        footer_frame = tk.Frame(main_frame, bg='#0d1117')
        footer_frame.pack(side='bottom', pady=20)

        tk.Label(
            footer_frame,
            text="Press ESC or F11 to toggle fullscreen • Updates every 10 seconds",
            font=('Segoe UI', 10),
            fg='#6e7681',
            bg='#0d1117'
        ).pack()

        self.loading_dots = 0
        self.animate_loading()

    def animate_loading(self):
        if self.current_price == 0:
            dots = "." * (self.loading_dots % 4)
            self.price_label.config(text=f"Loading{dots}")
            self.loading_dots += 1
            self.app.after(500, self.animate_loading)

    def get_btc_price(self):
        try:
            response = requests.get("https://indodax.com/api/ticker/btcidr", timeout=10)
            if response.status_code == 200:
                data = response.json()
                new_price = int(float(data['ticker']['last']))

                if self.current_price > 0:
                    self.previous_price = self.current_price
                    self.price_change = new_price - self.previous_price
                    if self.previous_price > 0:
                        self.price_change_percent = (self.price_change / self.previous_price) * 100

                self.current_price = new_price
                self.last_update = datetime.now().strftime("%H:%M:%S")
                self.update_ui()
                self.status_label.config(text="●  Live", fg='#3fb950')

            else:
                self.status_label.config(text="●  Error", fg='#f85149')

        except requests.exceptions.RequestException:
            self.status_label.config(text="●  No Connection", fg='#f85149')

        except Exception as e:
            self.status_label.config(text="●  Error", fg='#f85149')
            print(f"Error: {e}")

    def update_ui(self):
        if self.current_price > 0:
            formatted_price = f"{self.current_price:,}".replace(",", ".")
            self.price_label.config(text=f"Rp {formatted_price}")

            if self.price_change != 0:
                change_symbol = "+" if self.price_change > 0 else ""
                change_color = "#3fb950" if self.price_change > 0 else "#f85149"
                formatted_change = f"{abs(self.price_change):,}".replace(",", ".")
                change_text = f"{change_symbol}Rp {formatted_change} ({change_symbol}{self.price_change_percent:.2f}%)"
                self.change_label.config(text=change_text, fg=change_color)
                self.price_label.config(fg=change_color)
                self.app.after(1000, lambda: self.price_label.config(fg='#58a6ff'))

            self.update_label.config(text=self.last_update)

    def start_price_updates(self):
        def update_loop():
            while self.is_running:
                self.get_btc_price()
                time.sleep(10)

        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()

    def toggle_fullscreen(self, event=None):
        try:
            self.app.attributes('-fullscreen', not self.app.attributes('-fullscreen'))
        except:
            if self.app.state() == 'zoomed':
                self.app.state('normal')
            else:
                self.app.state('zoomed')

    def on_closing(self):
        self.is_running = False
        self.app.destroy()

    def run(self):
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app.mainloop()

if __name__ == "__main__":
    tracker = BitcoinPriceTracker()
    tracker.run()
