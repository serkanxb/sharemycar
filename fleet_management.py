# fleet_management.py
# Carsharing fleet management system for ShareMyCar
# Implements vehicle inventory, booking, returns, maintenance, transaction logs, and financial metrics.

import sqlite3  # SQLite database for persistent storage
import datetime  # For handling dates and times

class Database:
    """
    Wrapper around sqlite3 connection and setup.
    Initializes tables for vehicles, bookings, returns, transactions.
    """
    def __init__(self, db_file='sharemycar.db'):
        # Connect to the SQLite database (or create it)
        self.conn = sqlite3.connect(db_file)
        # Ensure foreign keys are enforced
        self.conn.execute('PRAGMA foreign_keys = ON;')
        # Create tables if they don't exist
        self._create_tables()

    def _create_tables(self):
        # Vehicles table: stores inventory
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id TEXT PRIMARY KEY,
            brand_model TEXT NOT NULL,
            mileage INTEGER NOT NULL,
            daily_price REAL NOT NULL,
            maint_cost_per_km REAL NOT NULL,
            status TEXT NOT NULL
        );
        ''')
        # Bookings table: records reservations
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            vehicle_id TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            est_km INTEGER NOT NULL,
            est_cost REAL NOT NULL,
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
        );
        ''')
        # Returns table: records returns and fees
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS returns (
            return_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            actual_km INTEGER NOT NULL,
            late_fee REAL NOT NULL,
            cleaning_fee REAL NOT NULL,
            maint_cost REAL NOT NULL,
            return_date TEXT NOT NULL,
            FOREIGN KEY(booking_id) REFERENCES bookings(booking_id)
        );
        ''')
        # Transactions table: financial log
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            vehicle_id TEXT NOT NULL,
            revenue REAL NOT NULL,
            cost REAL NOT NULL,
            trans_date TEXT NOT NULL
        );
        ''')
        # Commit the schema changes
        self.conn.commit()

# Further classes and methods will go here (Vehicle, FleetManager, BookingManager, ReturnProcessor, MaintenanceScheduler, FinancialMetrics)

if __name__ == '__main__':
    # Entry point: initialize database and launch CLI or other interface
    db = Database()
    print("ShareMyCar Fleet Management System initialized.")
    # TODO: Launch interactive menu
