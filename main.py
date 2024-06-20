from tkinter import *
from signup_screen import SignupScreen
from login_screen import LoginScreen
from home_screen import HomeScreen
from db import db_instance

class MainApp:
    def __init__(self, root):
        self.root = root
        self.signup_screen = None
        self.login_screen = None
        self.home_screen = None
        self.current_user = None  # To store the logged-in user information
        self.show_signup_screen()

    def show_signup_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.signup_screen = SignupScreen(self.root, self.show_login_screen)

    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.login_screen = LoginScreen(self.root, self.show_signup_screen, self.show_home_screen)

    def show_home_screen(self, user):
        self.current_user = user  # Store the logged-in user information
        for widget in self.root.winfo_children():
            widget.destroy()
        self.home_screen = HomeScreen(self.root, self.current_user, self.logout_callback)

    def logout_callback(self):
        self.current_user = None
        self.show_login_screen()

def main():
    db_instance.create_tables()
    
    root = Tk()
    root.geometry('720x480')
    root.minsize(720, 480)
    app = MainApp(root)
    app.show_signup_screen()
    root.mainloop()

if __name__ == "__main__":
    main()
