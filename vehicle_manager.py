#!/usr/bin/env python3
# vehicle_manager.py

import sqlite3                                  # For database operations
from database import create_connection          # Reuse our DB connection helper

class VehicleManager:
    """
    Handles all vehicle‐related operations:
      - Viewing inventory
      - Adding vehicles
      - Updating availability status
    """

    def __init__(self, db_file="sharemycar.db"):
        """
        Initialize the VehicleManager with a SQLite connection.

        :param db_file: Path to the SQLite database file.
        """
        # Create (or open) the database connection
        self.conn = create_connection(db_file)

    def view_inventory(self):
        """
        Retrieve and return all vehicles in the inventory.

        :return: List of dicts, each representing a vehicle.
        """
        cursor = self.conn.cursor()               # Get a cursor to execute SQL
        cursor.execute("SELECT * FROM vehicles;") # Select all columns from vehicles
        rows = cursor.fetchall()                  # Fetch all result rows

        # Transform rows into a list of dictionaries for easy use
        vehicles = []
        for row in rows:
            vehicles.append({
                'vehicle_id':        row[0],          # Unique vehicle identifier
                'brand_model':       row[1],          # Brand and model string
                'mileage':           row[2],          # Current odometer reading
                'daily_price':       row[3],          # Price per day in €
                'maint_cost_per_km': row[4],          # Cost per km in €
                'is_available':      bool(row[5])     # Availability as True/False
            })
        return vehicles

    def generate_vehicle_id(self):
        """
        Generate the next vehicle ID of the form 'V###',
        by finding the current highest numeric suffix and incrementing it.

        :return: A new unique vehicle_id string.
        """
        cursor = self.conn.cursor()
        # Select the vehicle_id with the highest numeric part
        cursor.execute("""
               SELECT vehicle_id
                 FROM vehicles
                WHERE vehicle_id LIKE 'V%'
                ORDER BY CAST(SUBSTR(vehicle_id, 2) AS INTEGER) DESC
                LIMIT 1;
           """)
        row = cursor.fetchone()
        last_num = int(row[0][1:]) if row else 0
        new_num = last_num + 1
        return f"V{new_num:03d}"

    def add_vehicle(self, vehicle_id, brand_model, mileage,
                    daily_price, maint_cost_per_km):
        """
        Insert a new vehicle into the fleet.

        :param vehicle_id:        String ID (e.g., "V011")
        :param brand_model:       Brand and model (e.g., "Tesla Model 3")
        :param mileage:           Initial odometer reading (int)
        :param daily_price:       Rental price per day (float)
        :param maint_cost_per_km: Maintenance cost per km (float)
        """
        cursor = self.conn.cursor()               # Prepare SQL execution
        cursor.execute(
            """
            INSERT INTO vehicles (
                vehicle_id, brand_model, mileage,
                daily_price, maint_cost_per_km, is_available
            ) VALUES (?, ?, ?, ?, ?, 1);
            """,
            (vehicle_id, brand_model, mileage,
             daily_price, maint_cost_per_km)
        )
        self.conn.commit()                        # Save changes to the DB

    def update_availability(self, vehicle_id, is_available):
        """
        Mark a vehicle as available or unavailable.

        :param vehicle_id:    String ID of the vehicle.
        :param is_available:  Boolean or int (True/1 for available, False/0 for unavailable).
        """
        cursor = self.conn.cursor()               # Prepare SQL execution
        cursor.execute(
            """
            UPDATE vehicles
            SET is_available = ?
            WHERE vehicle_id = ?;
            """,
            (1 if is_available else 0, vehicle_id)
        )
        self.conn.commit()                        # Save changes to the DB

# Quick manual test when run directly
if __name__ == "__main__":
    vm = VehicleManager()                        # Initialize Manager
    print("Current Inventory:")
    for v in vm.view_inventory():                # List all vehicles
        print(v)
    # Example: add a test vehicle, then mark it unavailable
    vm.add_vehicle("V011", "Test Car X", 100, 40.0, 0.15)
    vm.update_availability("V011", False)
    print("\nAfter Adding & Updating V011:")
    for v in vm.view_inventory():
        print(v)
