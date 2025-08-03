# hospital_system/gui_views/main_menu.py

import tkinter as tk
from tkinter import ttk
from . import admin_views
from . import pharmacist_views

class MainMenu(tk.Toplevel):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.title(f"HMS Main Menu - Welcome {self.user['username']} (Role: {self.user['role']})")
        self.geometry("500x400")
        
        self.create_widgets()

    def create_widgets(self):
        role = self.user['role']
        
        # A frame to hold the buttons
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(expand=True)

        if role == 'Admin':
            ttk.Button(button_frame, text="Manage Doctors", command=self.open_doctor_management).pack(pady=5, fill='x')
            ttk.Button(button_frame, text="Manage Staff", command=self.open_staff_management).pack(pady=5, fill='x')
        
        if role == 'Pharmacist':
            ttk.Button(button_frame, text="Manage Pharmacy Stock", command=self.open_pharmacy_management).pack(pady=5, fill='x')
            # Add other pharmacist buttons here...
            
        # Add other roles here...
        # if role == 'Receptionist':
        # ...
        
        ttk.Button(button_frame, text="Logout", command=self.destroy).pack(pady=20, fill='x')

    def open_doctor_management(self):
        admin_views.open_doctor_management_window(self)

    def open_pharmacy_management(self):
        pharmacist_views.open_pharmacy_management_window(self)
    def open_staff_management(self):
        admin_views.open_staff_management_window(self)
