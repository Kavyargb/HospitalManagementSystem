# hospital_system/gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from auth.login import check_credentials
from gui_views.main_menu import MainMenu

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HMS Login")
        self.geometry("300x150")
        
        self.create_login_widgets()

    def create_login_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        
        ttk.Label(self, text="Username:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.user_entry = ttk.Entry(self)
        self.user_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)

        ttk.Label(self, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.pass_entry = ttk.Entry(self, show="*")
        self.pass_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)

        ttk.Button(self, text="Login", command=self.handle_login).grid(row=2, column=0, columnspan=2, pady=10)

    def handle_login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        user = check_credentials(username, password)
        
        if user:
            self.withdraw() # Hide the login window
            MainMenu(self, user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

if __name__ == "__main__":
    app = App()
    app.mainloop()