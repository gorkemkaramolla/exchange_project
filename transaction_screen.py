from tkinter import *
from tkinter import ttk

class TransactionScreen:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        # Create a container frame
        container = ttk.Frame(self.root)
        container.place(anchor='center', relx=0.5, rely=0.5)

        frm = ttk.Frame(container)
        frm.grid(sticky='nsew')

        self.currency_combo = ttk.Combobox(frm, values=["USD", "EUR", "GMB"])
        self.currency_combo.set("Select currency")
        self.currency_combo.grid(row=0, column=0, sticky='nsew')
        self.currency_combo.bind("<<ComboboxSelected>>", self.enable_entry)

        self.money_entry = ttk.Entry(frm, justify=CENTER, state=DISABLED)
        self.money_entry.insert(0, "Enter the money")
        self.money_entry.grid(row=1, column=0, sticky='nsew')

        ttk.Button(frm, text="Para Yatır", command=self.handle_submit).grid(row=2, column=0, sticky='nsew')

        # Create a child frame
        child_frame = ttk.Frame()
        child_frame.grid(row=8, column=3, sticky='e')

        # Add a label with the text "Hello" to the child frame
        hello_label = ttk.Label(child_frame, text="Hello")
        hello_label.pack()

        # Configure the rows and columns to expand with the window
        frm.grid_columnconfigure(0, weight=1)
        for i in range(4):
            frm.grid_rowconfigure(i, weight=1)

    def handle_submit(self):
        print("Ended")

    def enable_entry(self, event):
        self.money_entry.config(state=NORMAL)