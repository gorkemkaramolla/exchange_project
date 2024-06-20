from tkinter import *
from tkinter import ttk, messagebox

from db import db_instance

class SignupScreen:
    def __init__(self, root, switch_to_login):
        self.root = root
        self.root.title("Kayıt Ol")
        self.switch_to_login = switch_to_login
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

        email_label = ttk.Label(container, text="Email")
        email_label.grid(row=2, column=0, sticky='w', pady=5)
        self.email_entry = ttk.Entry(container)
        self.email_entry.grid(row=2, column=1, sticky='ew', pady=5)

        signup_button = ttk.Button(container, text="Kayıt ol", command=self.handle_submit)
        signup_button.grid(row=3, columnspan=2, pady=10)

        login_link = ttk.Button(container, text="Zaten bir hesabın var mı? Giriş yap ", command=self.switch_to_login)
        login_link.grid(row=4, columnspan=2, pady=10)

        container.grid_columnconfigure(1, weight=1)

    def handle_submit(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()
        if not username or not password or not email:
            return
        db_instance.insert_user(username, password, email)
        messagebox.showinfo("Success", "Başarıyla kayıt olundu,lütfen giriş yapınız!")
        self.switch_to_login()
