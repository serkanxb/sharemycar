#!/usr/bin/env python3
# return_manager.py

import sqlite3                                  # SQLite library for DB operations
import datetime                                 # For parsing and handling dates
from database import create_connection          # Reuse our DB connection helper

class ReturnManager:
    """
    Handles processing of vehicle returns:
      - Recording actual kilometers driven
      - Calculating late fees, cleaning fees, and maintenance costs
      - Logging returns and transactions
      - Updating vehicle mileage and availability
    """

    CLEANING_FEE = 20.0      # Fixed cleaning fee per return (€)
    LATE_FEE_PER_DAY = 10.0  # Late fee per day (€)
    MAINT_THRESHOLD = 10000  # km interval for mandatory maintenance

    def __init__(self, db_file="sharemycar.db"):
        """
        Initialize ReturnManager with a SQLite connection.

        :param db_file: Path to the SQLite database file.
        """
        self.conn = create_connection(db_file)      # Open connection to DB

    def process_return(self, booking_id, actual_km, return_date_str):
        """
        Process a vehicle return.

        :param booking_id:       Integer ID of the booking being returned.
        :param actual_km:        Integer of kilometers driven during rental.
        :param return_date_str:  Return date as 'YYYY-MM-DD' string.
        :return:                 Dict summarizing all costs and info.
        :raises ValueError:      If booking not found or already returned.
        """
        cursor = self.conn.cursor()                # Prepare to run SQL

        # 1) Fetch booking + vehicle info
        cursor.execute(
            """
            SELECT 
              b.customer_name, b.vehicle_id, b.start_date, b.end_date,
              b.est_km, b.est_cost,
              v.mileage AS orig_mileage,
              v.maint_cost_per_km
            FROM bookings b
            JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            WHERE b.booking_id = ?;
            """,
            (booking_id,)
        )
        row = cursor.fetchone()                    # Read result
        if not row:
            raise ValueError(f"Booking ID {booking_id} not found.")  # No such booking

        # Unpack fetched data
        (customer_name, vehicle_id,
         start_date_str, end_date_str,
         est_km, est_cost,
         orig_mileage, maint_cost_per_km) = row

        # 2) Parse dates
        start_date      = datetime.date.fromisoformat(start_date_str)
        expected_return = datetime.date.fromisoformat(end_date_str)
        actual_return   = datetime.date.fromisoformat(return_date_str)

        # 3) Calculate late fees
        delta_days = (actual_return - expected_return).days  # Positive if late
        late_days  = delta_days if delta_days > 0 else 0    # No negative late days
        late_fee   = late_days * self.LATE_FEE_PER_DAY      # €10 per late day

        # 4) Cleaning fee is fixed
        clean_fee = self.CLEANING_FEE

        # 5) Maintenance cost = per‑km rate × actual kilometers driven
        maint_fee = actual_km * maint_cost_per_km

        # 6) Insert into returns table
        cursor.execute(
            """
            INSERT INTO returns (
                booking_id, actual_km, late_fee,
                clean_fee, maint_cost, return_date
            ) VALUES (?, ?, ?, ?, ?, ?);
            """,
            (booking_id, actual_km, late_fee,
             clean_fee, maint_fee, return_date_str)
        )

        # 7) Record in transactions log
        rental_days = (expected_return - start_date).days     # Original rental duration
        cursor.execute(
            """
            INSERT INTO transactions (
                customer_name, vehicle_id, rental_duration,
                revenue, cleaning_fee, maintenance_fee, late_fee, date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (customer_name, vehicle_id, rental_days,
             est_cost, clean_fee, maint_fee, late_fee, return_date_str)
        )

        # 8) Update vehicle mileage and mark it available
        new_mileage = orig_mileage + actual_km
        cursor.execute(
            """
            UPDATE vehicles
               SET mileage = ?, is_available = 1
             WHERE vehicle_id = ?;
            """,
            (new_mileage, vehicle_id)
        )

        # 9) Automatic maintenance logging (threshold = 10 000 km)
        #    We do NOT change is_available here.
        cursor.execute(
            "SELECT MAX(mileage_at_maint) FROM maintenance_log WHERE vehicle_id = ?;",
            (vehicle_id,)
        )
        last_maint = cursor.fetchone()[0] or 0
        km_since = new_mileage - last_maint

        maintenance_scheduled = False
        if km_since >= self.MAINT_THRESHOLD:
            maint_cost = km_since * maint_cost_per_km
            # Insert a maintenance log entry
            cursor.execute(
                """
                INSERT INTO maintenance_log (
                    vehicle_id, mileage_at_maint, cost, date
                ) VALUES (?, ?, ?, ?);
                """,
                (vehicle_id, new_mileage, maint_cost, return_date_str)
            )
            maintenance_scheduled = True

        # 10) Commit everything
        self.conn.commit()

        # 11) Return summary, including whether we logged maintenance
        return {
            "booking_id": booking_id,
            "customer_name": customer_name,
            "vehicle_id": vehicle_id,
            "return_date": return_date_str,
            "actual_km": actual_km,
            "late_days": late_days,
            "late_fee": late_fee,
            "cleaning_fee": clean_fee,
            "maintenance_fee": maint_fee,
            "total_additional": late_fee + clean_fee + maint_fee,
            "maintenance_scheduled": maintenance_scheduled,
            "revenue": est_cost,
            "rental_duration": rental_days
        }

    def view_returns(self):
        """
        Retrieve and return all processed returns.

        :return: List of dicts, each representing a return record.
        """
        cursor = self.conn.cursor()                 # Prepare to run SQL
        cursor.execute("SELECT * FROM returns;")    # Fetch all return rows
        rows = cursor.fetchall()                    # Read result set

        # Build list of return dicts
        results = []
        for (ret_id, booking_id, actual_km, late_fee,
             clean_fee, maint_cost, return_date) in rows:
            results.append({
                "return_id":    ret_id,
                "booking_id":   booking_id,
                "actual_km":    actual_km,
                "late_fee":     late_fee,
                "clean_fee":    clean_fee,
                "maint_cost":   maint_cost,
                "return_date":  return_date
            })
        return results

# Quick smoke test when run directly
if __name__ == "__main__":
    rm = ReturnManager()                           # Initialize manager
    print("Existing returns:")
    for r in rm.view_returns():                    # List processed returns
        print(r)

    # Example: process return for booking #1
    try:
        summary = rm.process_return(
            booking_id=1,                          # Booking ID to close
            actual_km=250,                         # Kilometers driven
            return_date_str="2025-04-27"           # Actual return date
        )
        print("\nReturn processed:")
        print(summary)
    except ValueError as e:
        print("Error:", e)
