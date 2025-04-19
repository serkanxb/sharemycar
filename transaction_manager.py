#!/usr/bin/env python3
# transaction_manager.py

import sqlite3
from database import create_connection  # Helper to get our SQLite connection

class TransactionManager:
    """
    Handles retrieval of the transaction log, which records:
      - Customer name
      - Vehicle ID
      - Rental duration
      - Revenue generated
      - Cleaning fee
      - Maintenance fee
      - Late fee
      - Date of transaction
    """

    def __init__(self, db_file="sharemycar.db"):
        """
        Initialize TransactionManager with a SQLite connection.

        :param db_file: Path to the SQLite database file.
        """
        # Open (or create) the database connection
        self.conn = create_connection(db_file)

    def view_transactions(self):
        """
        Retrieve and return all transaction records.

        :return: List of dicts, each representing one transaction.
        """
        cursor = self.conn.cursor()  # Prepare SQL execution
        cursor.execute("""
            SELECT 
              trans_id,
              customer_name,
              vehicle_id,
              rental_duration,
              revenue,
              cleaning_fee,
              maintenance_fee,
              late_fee,
              date
            FROM transactions;
        """)                          # Query all columns from transactions
        rows = cursor.fetchall()      # Fetch all result rows

        # Transform rows into a list of dictionaries
        transactions = []
        for (trans_id, customer_name, vehicle_id, rental_duration,
             revenue, cleaning_fee, maintenance_fee, late_fee, date) in rows:
            transactions.append({
                "trans_id":        trans_id,         # Unique transaction ID
                "customer_name":   customer_name,    # Name of the customer
                "vehicle_id":      vehicle_id,       # Vehicle involved
                "rental_duration": rental_duration,  # Days rented
                "revenue":         revenue,          # Booking revenue (€)
                "cleaning_fee":    cleaning_fee,     # Cleaning fee (€)
                "maintenance_fee": maintenance_fee,  # Maintenance fee (€)
                "late_fee":        late_fee,         # Late return fee (€)
                "date":            date              # Date of the transaction
            })
        return transactions

# Quick manual test when run directly
if __name__ == "__main__":
    tm = TransactionManager()               # Initialize the manager
    print("=== Transaction Log ===")
    for tx in tm.view_transactions():       # List all transactions
        print(tx)
