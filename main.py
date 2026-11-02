import tkinter as tk

import mw1

window = tk.Tk()
window.title("Visual Data Analysis")

tk.Button(
    window,
    text="Run MW.1 - Train",
    command=lambda: mw1.main("train"),
).pack(padx=30, pady=10)

tk.Button(
    window,
    text="Run MW.1 - Car",
    command=lambda: mw1.main("car"),
).pack(padx=30, pady=10)

window.mainloop()
