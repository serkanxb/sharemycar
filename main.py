#!/usr/bin/env python3
# main.py

"""
Main CLI application for ShareMyCar fleet management.
Presents a menu to perform all operations:
 1. View inventory
 2. Add vehicle
 3. Make booking
 4. Process return
 5. Schedule maintenance
 6. View maintenance log
 7. View transaction log
 8. View financial report
 9. Exit
"""

import sys
import datetime

# Import our modules
from database import initialize_database
from vehicle_manager import VehicleManager
from booking_manager import BookingManager
from return_manager import ReturnManager
from maintenance_scheduler import MaintenanceScheduler
from transaction_manager import TransactionManager
from financial_manager import FinancialManager

def main():
    """
    Initialize the database and managers, then loop on user commands.
    """
    # Ensure DB and tables exist, and seed vehicles if needed
    initialize_database()

    # Instantiate each manager
    vm = VehicleManager()            # For inventory operations
    bm = BookingManager()            # For bookings
    rm = ReturnManager()             # For returns
    ms = MaintenanceScheduler()      # For maintenance scheduling
    tm = TransactionManager()        # For viewing transactions
    fm = FinancialManager()          # For financial metrics

    # Main menu loop
    while True:
        # Display options
        print("\n=== ShareMyCar Management ===")
        print("1. View inventory")
        print("2. Add vehicle")
        print("3. Make booking")
        print("4. Process return")
        print("5. Schedule maintenance")
        print("6. View maintenance log")
        print("7. View transaction log")
        print("8. View financial report")
        print("9. Exit")

        choice = input("Select an option [1-9]: ").strip()  # Read user choice

        if choice == '1':
            # 1) View inventory
            inventory = vm.view_inventory()
            print("\n-- Vehicle Inventory --")
            for v in inventory:
                status = "Available" if v['is_available'] else "Unavailable"
                print(f"{v['vehicle_id']}: {v['brand_model']} | "
                      f"Mileage: {v['mileage']} km | €{v['daily_price']}/day | "
                      f"Maint €{v['maint_cost_per_km']}/km | {status}")

        elif choice == '2':
            # 2) Add vehicle
            vid   = input("Vehicle ID (leave blank to auto‑generate): ").strip()
            bmnl  = input("Brand & Model: ").strip()
            mil   = int(input("Starting mileage (km): ").strip())
            dprice= float(input("Daily price (€): ").strip())
            mcost = float(input("Maint cost per km (€): ").strip())

            # Auto-generate if blank

            if not vid:
                vid = vm.generate_vehicle_id()
                print(f"→ Generated Vehicle ID: {vid}")
            vm.add_vehicle(vid, bmnl, mil, dprice, mcost)
            print(f"Added vehicle {vid} successfully.")

        elif choice == '3':
            # 3) Make booking
            cname = input("Customer name: ").strip()
            vid   = input("Vehicle ID: ").strip()
            sdate = input("Start date (YYYY-MM-DD): ").strip()
            days  = int(input("Rental duration (days): ").strip())
            ekm   = int(input("Estimated km: ").strip())
            try:
                booking = bm.create_booking(cname, vid, sdate, days, ekm)
                print("\nBooking created:")
                for k, v in booking.items():
                    print(f"  {k}: {v}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == '4':
            # 4) Process return
            bid   = int(input("Booking ID to return: ").strip())
            akm   = int(input("Actual km driven: ").strip())
            rdate = input("Return date (YYYY-MM-DD): ").strip()
            try:
                summary = rm.process_return(bid, akm, rdate)
                print("\nReturn processed:")
                for k, v in summary.items():
                    print(f"  {k}: {v}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == '5':
            # 5) Schedule maintenance
            events = ms.schedule_maintenance()
            if events:
                print("\nMaintenance scheduled for:")
                for e in events:
                    print(f"  {e['vehicle_id']} at {e['date']} "
                          f"(mileage {e['mileage_at_maint']} km) cost €{e['cost']:.2f}")
            else:
                print("No vehicles require maintenance at this time.")

        elif choice == '6':
            # 6) View maintenance log
            log = ms.view_log()
            print("\n-- Maintenance Log --")
            for entry in log:
                print(f"{entry['maint_id']}: {entry['vehicle_id']} | "
                      f"{entry['mileage_at_maint']} km on {entry['date']} | "
                      f"€{entry['cost']:.2f}")

        elif choice == '7':
            # 7) View transaction log
            trans = tm.view_transactions()
            print("\n-- Transaction Log --")
            for t in trans:
                print(f"{t['trans_id']}: {t['customer_name']} | {t['vehicle_id']} | "
                      f"Days: {t['rental_duration']} | "
                      f"Rev €{t['revenue']:.2f} | "
                      f"Clean €{t['cleaning_fee']:.2f} | "
                      f"Maint €{t['maintenance_fee']:.2f} | "
                      f"Late €{t['late_fee']:.2f} on {t['date']}")

        elif choice == '8':
            # 8) View financial report
            report = fm.generate_full_report()
            print("\n=== Financial Report ===")
            print(f"Total Revenue:             €{report['total_revenue']:.2f}")
            print(f"Total Operational Costs:    €{report['total_operational_costs']:.2f}")
            print(f"Total Profit:               €{report['total_profit']:.2f}")
            print(f"Average Mileage per Vehicle:{report['average_mileage']:.2f} km")

        elif choice == '9':
            # 9) Exit
            print("Exiting ShareMyCar Management. Goodbye!")
            sys.exit(0)  # Graceful shutdown

        else:
            # Invalid input
            print("Invalid choice. Please enter a number from 1 to 9.")

if __name__ == "__main__":
    main()
