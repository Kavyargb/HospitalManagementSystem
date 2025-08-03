# hospital_system/gui_views/admin_views.py

import tkinter as tk
from tkinter import ttk, messagebox
from modules import doctors

from db.connection import execute_query
from auth.login import create_user 

def open_doctor_management_window(parent):
    window = tk.Toplevel(parent)
    window.title("Doctor Management")
    window.geometry("800x500")

    # --- Treeview for displaying doctors ---
    columns = ('id', 'name', 'specialization', 'contact', 'username')
    tree = ttk.Treeview(window, columns=columns, show='headings')
    
    # Define headings
    tree.heading('id', text='ID')
    tree.heading('name', text='Name')
    tree.heading('specialization', text='Specialization')
    tree.heading('contact', text='Contact')
    tree.heading('username', text='Username')
    
    # Adjust column widths
    tree.column('id', width=50)
    tree.column('name', width=200)
    tree.column('specialization', width=150)
    tree.column('contact', width=120)
    tree.column('username', width=120)

    def populate_doctors():
        # Clear existing items
        for i in tree.get_children():
            tree.delete(i)
        # Fetch and insert new items
        doctor_list = doctors.list_all_doctors() # This function prints, but also returns data
        if doctor_list:
            for doc in doctor_list:
                tree.insert('', tk.END, values=(doc['id'], doc['name'], doc['specialization'], doc['contact'], doc['username']))

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # --- Right-side frame for buttons ---
    button_frame = ttk.Frame(window, padding="10")
    button_frame.pack(side=tk.RIGHT, fill=tk.Y)
    
    ttk.Button(button_frame, text="Add New Doctor", command=lambda: open_add_doctor_form(window, populate_doctors)).pack(pady=5)
    ttk.Button(button_frame, text="Refresh List", command=populate_doctors).pack(pady=5)
    
    populate_doctors() # Initial population

def open_add_doctor_form(parent, refresh_callback):
    form = tk.Toplevel(parent)
    form.title("Add New Doctor")
    form.geometry("350x250")

    fields = ['Full Name', 'Specialization', 'Contact', 'Username', 'Password']
    entries = {}
    
    for i, field in enumerate(fields):
        ttk.Label(form, text=field + ":").grid(row=i, column=0, padx=10, pady=5, sticky='w')
        entry = ttk.Entry(form, show="*" if field == 'Password' else "")
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[field] = entry

    def save_doctor():
        name = entries['Full Name'].get()
        spec = entries['Specialization'].get()
        contact = entries['Contact'].get()
        username = entries['Username'].get()
        password = entries['Password'].get()

        if not all([name, spec, contact, username, password]):
            messagebox.showerror("Error", "All fields are required.", parent=form)
            return

        # Call the non-interactive backend function
        new_doc_id = doctors.create_doctor_profile(name, spec, contact, username, password)
        if new_doc_id:
            messagebox.showinfo("Success", f"Doctor '{name}' added successfully!", parent=form)
            form.destroy()
            refresh_callback() # Refresh the doctor list in the parent window
        else:
            messagebox.showerror("Error", "Failed to add doctor. Username may be taken.", parent=form)

    ttk.Button(form, text="Save", command=save_doctor).grid(row=len(fields), columnspan=2, pady=10)

    from auth.login import create_user # Import the backend function

def open_staff_management_window(parent):
    window = tk.Toplevel(parent)
    window.title("Staff Management")
    window.geometry("600x400")

    # --- Treeview for displaying staff ---
    columns = ('id', 'username', 'role')
    tree = ttk.Treeview(window, columns=columns, show='headings')
    tree.heading('id', text='ID')
    tree.heading('username', text='Username')
    tree.heading('role', text='Role')
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def populate_staff():
        for i in tree.get_children():
            tree.delete(i)
        # Fetch non-doctor, non-admin staff
        query = "SELECT id, username, role FROM users WHERE role NOT IN ('Admin', 'Doctor')"
        staff_list = execute_query(query, fetch='all')
        if staff_list:
            for member in staff_list:
                tree.insert('', tk.END, values=(member['id'], member['username'], member['role']))
    
    # --- Frame for buttons ---
    button_frame = ttk.Frame(window, padding="10")
    button_frame.pack(fill=tk.X)
    
    ttk.Button(button_frame, text="Add New Staff Member", command=lambda: open_add_staff_form(window, populate_staff)).pack(side=tk.LEFT)
    ttk.Button(button_frame, text="Refresh List", command=populate_staff).pack(side=tk.LEFT, padx=10)
    
    populate_staff()

def open_add_staff_form(parent, refresh_callback):
    form = tk.Toplevel(parent)
    form.title("Add New Staff Member")
    form.geometry("350x200")

    # --- Widgets for the form ---
    form_frame = ttk.Frame(form, padding="10")
    form_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
    username_entry = ttk.Entry(form_frame)
    username_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

    ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
    password_entry = ttk.Entry(form_frame, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

    ttk.Label(form_frame, text="Role:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
    role_combobox = ttk.Combobox(form_frame, state="readonly", values=['Receptionist', 'Pharmacist', 'Lab Tech'])
    role_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
    role_combobox.set('Receptionist') # Default value

    def save_staff_member():
        username = username_entry.get()
        password = password_entry.get()
        role = role_combobox.get()
        
        if not all([username, password, role]):
            messagebox.showerror("Error", "All fields are required.", parent=form)
            return

        # Use the non-interactive backend function
        user_id = create_user(username, password, role)
        if user_id:
            messagebox.showinfo("Success", f"User '{username}' created successfully!", parent=form)
            form.destroy()
            refresh_callback() # Update the list in the parent window
        else:
            # create_user prints errors to console, but let's give GUI feedback too
            messagebox.showerror("Error", "Failed to create user. Username may already exist.", parent=form)

    ttk.Button(form_frame, text="Save", command=save_staff_member).grid(row=3, columnspan=2, pady=10)
