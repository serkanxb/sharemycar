#!/usr/bin/env python3
# booking_manager.py

import sqlite3  # SQLite library for database operations
import datetime  # For date parsing and arithmetic
from database import create_connection  # Reuse our DB connection helper


class BookingManager:
    """
    Handles all booking operations:
      - Creating a new booking
      - Estimating cost
      - Marking vehicles unavailable
      - Viewing existing bookings
    """

    def __init__(self, db_file="sharemycar.db"):
        """
        Initialize the BookingManager with a SQLite connection.

        :param db_file: Path to the SQLite database file.
        """
        # Create (or open) the database connection
        self.conn = create_connection(db_file)

    def create_booking(self, customer_name, vehicle_id,
                       start_date_str, rental_days, est_km):
        """
        Create a new booking for a given vehicle.

        :param customer_name:   Name of the customer (string).
        :param vehicle_id:      ID of the vehicle to book (string).
        :param start_date_str:  Rental start date in 'YYYY-MM-DD' format (string).
        :param rental_days:     Duration of rental in days (int).
        :param est_km:          Estimated kilometers to be driven (int).
        :return:                Dict with booking details, including estimated cost.
        :raises ValueError:     If vehicle not found or not available.
        """
        cursor = self.conn.cursor()  # Prepare SQL execution

        # 1) Check vehicle's availability and pricing
        cursor.execute(
            """
            SELECT is_available, daily_price, maint_cost_per_km
              FROM vehicles
             WHERE vehicle_id = ?;
            """,
            (vehicle_id,)
        )
        row = cursor.fetchone()  # Fetch the result
        if not row:
            raise ValueError(f"Vehicle '{vehicle_id}' not found.")  # No such vehicle
        is_available, daily_price, maint_cost_per_km = row
        if not is_available:
            raise ValueError(f"Vehicle '{vehicle_id}' is currently unavailable.")  # Already booked

        # 2) Parse and compute dates
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        # Rental ends at end of last day (i.e., start + rental_days)
        end_date = start_date + datetime.timedelta(days=rental_days)

        # 3) Estimate cost: (days × daily price) + (km × maintenance cost per km)
        est_cost = (rental_days * daily_price) + (est_km * maint_cost_per_km)

        # 4) Insert booking into the bookings table
        cursor.execute(
            """
            INSERT INTO bookings (
                customer_name, vehicle_id,
                start_date, end_date,
                est_km, est_cost
            ) VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                customer_name,
                vehicle_id,
                start_date.isoformat(),
                end_date.isoformat(),
                est_km,
                est_cost
            )
        )
        booking_id = cursor.lastrowid  # Get the auto-generated booking ID

        # 5) Mark the vehicle as unavailable for the duration
        cursor.execute(
            """
            UPDATE vehicles
               SET is_available = 0
             WHERE vehicle_id = ?;
            """,
            (vehicle_id,)
        )

        # 6) Commit all changes to the database
        self.conn.commit()

        # 7) Return a summary of the created booking
        return {
            "booking_id": booking_id,
            "customer_name": customer_name,
            "vehicle_id": vehicle_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "est_km": est_km,
            "est_cost": est_cost
        }

    def view_bookings(self):
        """
        Retrieve all current bookings from the database.

        :return: List of dicts, each representing a booking record.
        """
        cursor = self.conn.cursor()  # Prepare SQL execution
        cursor.execute("SELECT * FROM bookings;")  # Select all columns
        rows = cursor.fetchall()  # Fetch all booking rows

        # Transform each row into a dict for easy use
        bookings = []
        for row in rows:
            bookings.append({
                "booking_id": row[0],  # Auto-incremented booking ID
                "customer_name": row[1],
                "vehicle_id": row[2],
                "start_date": row[3],
                "end_date": row[4],
                "est_km": row[5],
                "est_cost": row[6]
            })
        return bookings


# Quick manual test when run directly
if __name__ == "__main__":
    bm = BookingManager()  # Initialize BookingManager
    print("Existing bookings:")
    for b in bm.view_bookings():  # List all bookings
        print(b)

    # Example: create a new booking
    try:
        new_booking = bm.create_booking(
            "Alice Smith",  # Customer name
            "V002",  # Vehicle ID
            "2025-04-20",  # Start date
            5,  # Rental duration (days)
            200  # Estimated kilometers
        )
        print("\nNew booking created:")
        print(new_booking)
    except ValueError as e:
        print("\nError creating booking:", e)
