#!/usr/bin/env python3
# financial_manager.py

import sqlite3                                # For SQLite database operations
from database import create_connection        # Reuse our DB connection helper

class FinancialManager:
    """
    Provides real-time financial metrics:
      - Total revenue
      - Total operational costs (cleaning + maintenance + late fees)
      - Total profit (revenue - costs)
      - Average mileage per vehicle
    """

    def __init__(self, db_file="sharemycar.db"):
        """
        Initialize the FinancialManager by opening a database connection.

        :param db_file: Path to the SQLite database file.
        """
        self.conn = create_connection(db_file)  # Create (or open) the database

    def get_total_revenue(self):
        """
        Calculate total revenue from all completed transactions.

        :return: Float sum of the 'revenue' column from transactions.
        """
        cursor = self.conn.cursor()            # Prepare SQL execution
        cursor.execute("SELECT SUM(revenue) FROM transactions;")  # Sum up revenue
        result = cursor.fetchone()[0]          # Fetch the scalar result
        return result if result is not None else 0.0  # Default to 0.0 if no rows

    def get_total_operational_costs(self):
        """
        Calculate total operational costs: cleaning + maintenance + late fees.

        :return: Float sum of cleaning_fee + maintenance_fee + late_fee.
        """
        cursor = self.conn.cursor()            # Prepare SQL execution
        cursor.execute(
            """
            SELECT SUM(cleaning_fee + maintenance_fee + late_fee)
              FROM transactions;
            """
        )                                      # Sum all cost columns in one go
        result = cursor.fetchone()[0]          # Fetch the scalar result
        return result if result is not None else 0.0  # Default to 0.0 if no rows

    def get_total_profit(self):
        """
        Calculate total profit: revenue minus operational costs.

        :return: Float value of profit.
        """
        revenue = self.get_total_revenue()     # Fetch total revenue
        costs   = self.get_total_operational_costs()  # Fetch total costs
        return revenue - costs                 # Compute profit

    def get_average_mileage(self):
        """
        Calculate the average mileage across all vehicles in the fleet.

        :return: Float average of the 'mileage' column in vehicles.
        """
        cursor = self.conn.cursor()            # Prepare SQL execution
        cursor.execute("SELECT AVG(mileage) FROM vehicles;")  # Compute average
        result = cursor.fetchone()[0]          # Fetch the scalar result
        return result if result is not None else 0.0  # Default to 0.0 if no rows

    def generate_full_report(self):
        """
        Generate a consolidated financial report.

        :return: Dict containing all key metrics.
        """
        return {
            "total_revenue":            self.get_total_revenue(),
            "total_operational_costs":  self.get_total_operational_costs(),
            "total_profit":             self.get_total_profit(),
            "average_mileage":          self.get_average_mileage()
        }

if __name__ == "__main__":
    # Quick CLI test when run directly
    fm = FinancialManager()                   # Initialize the manager
    report = fm.generate_full_report()        # Build the full report

    # Print out each metric
    print("=== Financial Report ===")
    print(f"Total Revenue:             €{report['total_revenue']:.2f}")
    print(f"Total Operational Costs:    €{report['total_operational_costs']:.2f}")
    print(f"Total Profit:               €{report['total_profit']:.2f}")
    print(f"Average Mileage per Vehicle:{report['average_mileage']:.2f} km")
