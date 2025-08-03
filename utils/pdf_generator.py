# hospital_system/utils/pdf_generator.py

import os
from fpdf import FPDF
from datetime import datetime
from db.connection import execute_query

# Ensure a directory for reports exists
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_revenue_report():
    """Queries the database and generates a PDF revenue report."""
    print("-> Generating revenue report...")
    
    # 1. Fetch data
    query = """
        SELECT b.id, p.name, b.total_amount, b.bill_date
        FROM bills b JOIN patients p ON b.patient_id = p.id
        WHERE b.payment_status = 'Paid'
        ORDER BY b.bill_date
    """
    paid_bills = execute_query(query, fetch='all')
    
    if not paid_bills:
        print("<- No paid bills found to generate a report.")
        return

    # 2. Create PDF document
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Hospital Revenue Report", 0, 1, 'C')
    pdf.cell(0, 5, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
    pdf.ln(10) # Add a line break
    
    # Table Header
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(20, 10, 'Bill ID', 1, 0, 'C')
    pdf.cell(80, 10, 'Patient Name', 1, 0, 'C')
    pdf.cell(40, 10, 'Amount Paid', 1, 0, 'C')
    pdf.cell(40, 10, 'Date', 1, 1, 'C')
    
    # Table Rows
    pdf.set_font("Arial", '', 10)
    total_revenue = 0
    for bill in paid_bills:
        pdf.cell(20, 10, str(bill['id']), 1, 0, 'C')
        pdf.cell(80, 10, bill['name'], 1, 0)
        pdf.cell(40, 10, f"${bill['total_amount']:.2f}", 1, 0, 'R')
        pdf.cell(40, 10, str(bill['bill_date'].date()), 1, 1, 'C')
        total_revenue += bill['total_amount']
        
    # Total
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, 'Total Revenue:', 0, 0, 'R')
    pdf.cell(40, 10, f"${total_revenue:.2f}", 1, 1, 'R')

    # 3. Save PDF
    filename = os.path.join(REPORTS_DIR, f"revenue_report_{datetime.now().strftime('%Y%m%d')}.pdf")
    pdf.output(filename)
    
    print(f"✅ Report successfully saved to: {filename}")