import re
from datetime import datetime

def is_valid_phone(phone):
    """Validates a basic phone number format (7-15 digits)."""
    return phone.isdigit() and 7 <= len(phone) <= 15

def is_valid_date(date_str, fmt="%Y-%m-%d"):
    """Validates a date string against a format."""
    try:
        datetime.strptime(date_str, fmt)
        return True
    except ValueError:
        return False

def get_validated_input(prompt, validation_func, error_message):
    """A generic function to keep asking for input until it's valid."""
    while True:
        user_input = input(prompt)
        if validation_func(user_input):
            return user_input
        else:
            print(f"Invalid input: {error_message}")