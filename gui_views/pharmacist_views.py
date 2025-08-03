# hospital_system/gui_views/pharmacist_views.py

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db.connection import execute_query
# --- Add these imports for threading ---
import threading
import queue
# --- Import the backend module ---
from modules import pharmacy 

def open_pharmacy_management_window(parent):
    window = tk.Toplevel(parent)
    window.title("Pharmacy Management")
    window.geometry("900x600")

    # --- Top frame for buttons ---
    top_frame = ttk.Frame(window, padding=(10, 10, 10, 0))
    top_frame.pack(fill=tk.X)
    
    # --- Left frame for Treeview ---
    left_frame = ttk.Frame(window)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Right frame for image display ---
    right_frame = ttk.Frame(window, padding="10")
    right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
    
    ttk.Label(right_frame, text="Molecule Structure").pack()
    image_label = ttk.Label(right_frame, relief="solid", borderwidth=1)
    image_label.pack(pady=10, ipadx=5, ipady=5)
    
    # --- Treeview Setup ---
    columns = ('id', 'name', 'quantity', 'price')
    tree = ttk.Treeview(left_frame, columns=columns, show='headings')
    tree.heading('id', text='ID')
    tree.heading('name', text='Name')
    tree.heading('quantity', text='Quantity')
    tree.heading('price', text='Price')
    tree.pack(fill=tk.BOTH, expand=True)

    def populate_medicines():
        # Clear the treeview before populating
        for i in tree.get_children():
            tree.delete(i)
        medicines = execute_query("SELECT id, name, quantity, price FROM medicines ORDER BY name", fetch='all')
        if medicines:
            for med in medicines:
                tree.insert('', tk.END, values=(med['id'], med['name'], med['quantity'], f"{med['price']:.2f}"))

    # Add the buttons to the top frame
    ttk.Button(top_frame, text="Add New Medicine", 
               command=lambda: open_add_medicine_form(window, populate_medicines)).pack(side=tk.LEFT)
    ttk.Button(top_frame, text="Refresh List", command=populate_medicines).pack(side=tk.LEFT, padx=10)

    def show_molecule(event):
        # ... (this function remains the same as before)
        selected_item = tree.focus()
        if not selected_item: return
        med_id = tree.item(selected_item)['values'][0]
        med = execute_query("SELECT image_path, name FROM medicines WHERE id = %s", (med_id,), fetch='one')
        if med and med['image_path']:
            try:
                img = Image.open(med['image_path']); img.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(img); image_label.config(image=photo); image_label.image = photo
            except FileNotFoundError:
                image_label.config(image=None, text=f"Image not found\nfor {med['name']}")
        else:
            image_label.config(image=None, text=f"No image available\nfor {med['name']}")


    tree.bind('<<TreeviewSelect>>', show_molecule)
    populate_medicines() # Initial load

def open_add_medicine_form(parent, refresh_callback):
    form = tk.Toplevel(parent)
    form.title("Add New Medicine")
    form.geometry("400x250")

    fields = ['Name', 'Quantity', 'Price (e.g., 10.50)', 'Expiry Date (YYYY-MM-DD)']
    entries = {}
    
    frame = ttk.Frame(form, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)

    for i, field in enumerate(fields):
        ttk.Label(frame, text=field + ":").grid(row=i, column=0, padx=5, pady=5, sticky='w')
        entry = ttk.Entry(frame)
        entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
        entries[field] = entry
    
    # Queue for thread communication
    result_queue = queue.Queue()

    def process_queue():
        """Check the queue for a result from the worker thread."""
        try:
            result = result_queue.get_nowait()
            if result:
                messagebox.showinfo("Success", "Medicine added successfully!", parent=form)
                form.destroy()
                refresh_callback() # Refresh the main list
            else:
                messagebox.showerror("Error", "Failed to add medicine. Check console for details.", parent=form)
                save_button.config(state="normal", text="Save") # Re-enable button on failure
        except queue.Empty:
            form.after(100, process_queue) # Check again after 100ms

    def worker_thread_task(name, qty, price, expiry):
        """The task that runs in the background thread."""
        success = pharmacy.add_medicine_to_db(name, qty, price, expiry)
        result_queue.put(success)

    def save_medicine():
        # Get data from form
        name = entries['Name'].get()
        quantity = entries['Quantity'].get()
        price = entries['Price (e.g., 10.50)'].get()
        expiry_date = entries['Expiry Date (YYYY-MM-DD)'].get()

        if not all([name, quantity, price, expiry_date]):
            messagebox.showerror("Error", "All fields are required.", parent=form)
            return
        
        # Disable button to prevent multiple clicks
        save_button.config(state="disabled", text="Saving...")
        
        # Start the background thread
        threading.Thread(target=worker_thread_task, args=(name, quantity, price, expiry_date)).start()
        
        # Start polling the queue for the result
        form.after(100, process_queue)

    save_button = ttk.Button(frame, text="Save", command=save_medicine)
    save_button.grid(row=len(fields), columnspan=2, pady=20)