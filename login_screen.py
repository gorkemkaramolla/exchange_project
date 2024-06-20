# login_screen.py
from tkinter import *
from tkinter import ttk, messagebox
from db import db_cursor

class LoginScreen:
    def __init__(self, root, switch_to_signup, switch_to_home):
        self.root = root
        self.root.title("Giriş Yap")
        self.switch_to_signup = switch_to_signup
        self.switch_to_home = switch_to_home
        self.setup_ui()

    def setup_ui(self):
        container = ttk.Frame(self.root, padding=20)
        container.place(anchor='center', relx=0.5, rely=0.5)

        username_label = ttk.Label(container, text="Kullanıcı adı")
        username_label.grid(row=0, column=0, sticky='w', pady=5)
        self.username_entry = ttk.Entry(container)
        self.username_entry.grid(row=0, column=1, sticky='ew', pady=5)

        password_label = ttk.Label(container, text="Şifre")
        password_label.grid(row=1, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(container, show="*")
        self.password_entry.grid(row=1, column=1, sticky='ew', pady=5)

        login_button = ttk.Button(container, text="Giriş yap", command=self.handle_submit)
        login_button.grid(row=2, columnspan=2, pady=10)

        signup_link = ttk.Button(container, text="Bir hesabın yok mu? Kayıt ol", command=self.switch_to_signup)
        signup_link.grid(row=3, columnspan=2, pady=10)

        container.grid_columnconfigure(1, weight=1)

    def handle_submit(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        db_cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = db_cursor.fetchone()
        if user is not None:
            self.switch_to_home(user)  # Pass the user info to the home screen
        else:
            messagebox.showerror("Error", "Kullanıcı adı veya şifre hatalı!")
