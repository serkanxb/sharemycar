#!/usr/bin/env python3
# database.py
import os
import sqlite3  # Import SQLite library for DB operations
import sys


def get_db_path(filename="sharemycar.db"):
    """
    Returns the path to sharemycar.db in the same folder
    as the running script or exe.
    """
    if getattr(sys, 'frozen', False):
        # we’re running in a PyInstaller bundle
        base_dir = os.path.dirname(sys.executable)
    else:
        # running in a normal Python environment
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)


def create_connection(db_file):
    """
    Create a database connection to the SQLite database specified by db_file.

    :param db_file: String path to the SQLite database file.
    :return: sqlite3.Connection object or None if connection fails.
    """
    try:
        conn = sqlite3.connect(db_file)  # Attempt to connect (or create) the database file
        return conn  # Return the connection object on success
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")  # Print error message if connection fails
        return None  # Return None to signal failure


def create_tables(conn):
    """
    Create all required tables for the ShareMyCar system if they don't already exist.

    :param conn: sqlite3.Connection object
    """
    cursor = conn.cursor()  # Get a cursor for executing SQL commands

    # Create vehicles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id TEXT PRIMARY KEY,         -- Unique ID for each vehicle
            brand_model TEXT NOT NULL,           -- Brand and model description
            mileage INTEGER NOT NULL,            -- Total kilometers driven
            daily_price REAL NOT NULL,           -- Rental price per day
            maint_cost_per_km REAL NOT NULL,     -- Maintenance cost per kilometer
            is_available INTEGER NOT NULL       -- Availability flag: 1 = available, 0 = unavailable
        );
    """)  # Execute table creation SQL
    # Create bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-increment booking ID
            customer_name TEXT NOT NULL,                   -- Name of the customer
            vehicle_id TEXT NOT NULL,                      -- Vehicle being booked
            start_date TEXT NOT NULL,                      -- Rental start date (ISO format)
            end_date TEXT NOT NULL,                        -- Rental end date (ISO format)
            est_km INTEGER NOT NULL,                       -- Estimated kilometers to be driven
            est_cost REAL NOT NULL,                        -- Estimated rental cost
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
        );
    """)  # Execute table creation SQL
    # Create returns table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS returns (
            return_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Auto-increment return ID
            booking_id INTEGER NOT NULL,                   -- Reference to the booking
            actual_km INTEGER NOT NULL,                    -- Actual kilometers driven
            late_fee REAL NOT NULL,                        -- Fee for late return
            clean_fee REAL NOT NULL,                       -- Cleaning fee (fixed)
            maint_cost REAL NOT NULL,                      -- Maintenance cost calculated
            return_date TEXT NOT NULL,                     -- Actual return date (ISO format)
            FOREIGN KEY(booking_id) REFERENCES bookings(booking_id)
        );
    """)  # Execute table creation SQL
    # Create maintenance log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_log (
            maint_id INTEGER PRIMARY KEY AUTOINCREMENT,    -- Auto-increment maintenance ID
            vehicle_id TEXT NOT NULL,                      -- Vehicle undergoing maintenance
            mileage_at_maint INTEGER NOT NULL,             -- Odometer reading at service
            cost REAL NOT NULL,                            -- Cost of maintenance
            date TEXT NOT NULL,                            -- Date of maintenance (ISO format)
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
        );
    """)  # Execute table creation SQL
    # Create transaction logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            trans_id INTEGER PRIMARY KEY AUTOINCREMENT,    -- Auto-increment transaction ID
            customer_name TEXT NOT NULL,                   -- Customer involved
            vehicle_id TEXT NOT NULL,                      -- Vehicle involved
            rental_duration INTEGER NOT NULL,              -- Days rented
            revenue REAL NOT NULL,                         -- Revenue from booking
            cleaning_fee REAL NOT NULL,                    -- Cleaning fee charged
            maintenance_fee REAL NOT NULL,                 -- Maintenance fee charged
            late_fee REAL NOT NULL,                        -- Late fee charged
            date TEXT NOT NULL,                            -- Date of transaction (ISO format)
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
        );
    """)  # Execute table creation SQL

    conn.commit()  # Save (commit) all changes to the database


def seed_vehicles(conn):
    """
    Insert 10 sample vehicles into the vehicles table if it is currently empty.

    :param conn: sqlite3.Connection object
    """
    cursor = conn.cursor()  # Get a cursor for executing SQL commands
    cursor.execute("SELECT COUNT(*) FROM vehicles;")  # Query how many vehicles exist
    count = cursor.fetchone()[0]  # Fetch the count result

    if count == 0:  # Only seed if table is empty
        vehicles = [
            ("V001", "Toyota Corolla", 0, 30.0, 0.10, 1),
            ("V002", "Honda Civic", 0, 32.0, 0.12, 1),
            ("V003", "Ford Focus", 0, 28.0, 0.11, 1),
            ("V004", "BMW 3 Series", 0, 55.0, 0.20, 1),
            ("V005", "Audi A4", 0, 60.0, 0.22, 1),
            ("V006", "Volkswagen Golf", 0, 29.0, 0.10, 1),
            ("V007", "Mazda 3", 0, 31.0, 0.13, 1),
            ("V008", "Hyundai Elantra", 0, 27.0, 0.09, 1),
            ("V009", "Kia Forte", 0, 26.0, 0.08, 1),
            ("V010", "Chevrolet Cruze", 0, 25.0, 0.07, 1),
        ]  # List of 10 tuples matching table columns
        cursor.executemany(
            """
            INSERT INTO vehicles (
                vehicle_id, brand_model, mileage, daily_price,
                maint_cost_per_km, is_available
            ) VALUES (?, ?, ?, ?, ?, ?);
            """,
            vehicles  # Insert all sample rows at once
        )
        conn.commit()  # Commit after inserting seed data
        print("Seeded 10 sample vehicles into 'vehicles' table.")  # Inform user


def initialize_database(db_file="sharemycar.db"):
    """
    Full initialization: connect to DB, create tables, seed data, and close connection.

    :param db_file: Path for the SQLite database file (default: sharemycar.db)
    """
    conn = create_connection(db_file)  # Create/open the database
    if db_file is None:
        db_file = get_db_path()
    if conn:  # If connection succeeded
        create_tables(conn)  # Create all tables
        seed_vehicles(conn)  # Seed sample vehicles
        conn.close()  # Close connection gracefully
        print(f"Database initialized at '{db_file}'.")  # Confirmation message
    else:
        print("Failed to initialize database.")  # Error message on failure


if __name__ == "__main__":
    initialize_database()  # Run initialization when executed as a script
