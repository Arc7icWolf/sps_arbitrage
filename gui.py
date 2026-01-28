# gui.py
import tkinter as tk
import threading
import asyncio
from signals import main as bot_main

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("SPS Arbitrage Monitor")

        self.text = tk.Text(root, height=25, width=90)
        self.text.pack(padx=10, pady=10)

        self.start_btn = tk.Button(root, text="▶ Start", command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(root, text="⏹ Stop", command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.loop = None
        self.thread = None

    def log(self, msg):
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)

    def start(self):
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        def runner():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(bot_main(self.log))

        self.thread = threading.Thread(target=runner, daemon=True)
        self.thread.start()

    def stop(self):
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

root = tk.Tk()
app = App(root)
root.mainloop()
