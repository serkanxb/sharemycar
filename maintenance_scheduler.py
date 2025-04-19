#!/usr/bin/env python3
# maintenance_scheduler.py

import sqlite3
import datetime
from database import create_connection  # DB helper from database.py

class MaintenanceScheduler:
    """
    Automatically schedules and logs maintenance for vehicles
    when they exceed a mileage threshold.
    """

    def __init__(self, db_file="sharemycar.db"):
        """
        Initialize the scheduler with a SQLite connection.

        :param db_file: Path to the SQLite database file.
        """
        self.conn = create_connection(db_file)

    def schedule_maintenance(self, threshold_km=10000):
        """
        Scan all vehicles. For each, check the mileage since its last maintenance;
        if it exceeds `threshold_km`, log a maintenance event today
        and mark the vehicle unavailable.

        :param threshold_km: Mileage interval for service (int, default 10000).
        :return: List of dicts for each maintenance event created.
        """
        cursor = self.conn.cursor()

        # 1) Fetch each vehicle's current mileage and its maintenance rate
        cursor.execute("""
            SELECT vehicle_id, mileage, maint_cost_per_km
              FROM vehicles;
        """)
        vehicles = cursor.fetchall()

        created = []  # will hold any maintenance records we create

        for vehicle_id, mileage, maint_cost_per_km in vehicles:
            # 2) Find the mileage at last maintenance (or 0 if never maintained)
            cursor.execute("""
                SELECT MAX(mileage_at_maint)
                  FROM maintenance_log
                 WHERE vehicle_id = ?;
            """, (vehicle_id,))
            last_maint = cursor.fetchone()[0] or 0

            # 3) Compute how many km since last service
            km_since = mileage - last_maint

            # 4) If it's time for service, log it and mark unavailable
            if km_since >= threshold_km:
                cost = km_since * maint_cost_per_km            # € per km
                today = datetime.date.today().isoformat()       # e.g. "2025-04-19"

                # Insert a new maintenance_log entry
                cursor.execute("""
                    INSERT INTO maintenance_log (
                        vehicle_id, mileage_at_maint, cost, date
                    ) VALUES (?, ?, ?, ?);
                """, (vehicle_id, mileage, cost, today))

                # Mark the vehicle unavailable until maintenance is actually completed
                cursor.execute("""
                    UPDATE vehicles
                       SET is_available = 0
                     WHERE vehicle_id = ?;
                """, (vehicle_id,))

                # Record what we did
                created.append({
                    "vehicle_id": vehicle_id,
                    "mileage_at_maint": mileage,
                    "cost": cost,
                    "date": today
                })

        self.conn.commit()  # Persist all inserts/updates
        return created

    def view_log(self):
        """
        Retrieve the full maintenance history log.

        :return: List of dicts, each with keys:
                 maint_id, vehicle_id, mileage_at_maint, cost, date
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM maintenance_log;")
        rows = cursor.fetchall()

        log = []
        for (maint_id, vehicle_id, mileage_at_maint, cost, date) in rows:
            log.append({
                "maint_id": maint_id,
                "vehicle_id": vehicle_id,
                "mileage_at_maint": mileage_at_maint,
                "cost": cost,
                "date": date
            })
        return log

    def complete_maintenance(self, vehicle_id):
        """
        After servicing a vehicle, mark it available again.

        :param vehicle_id: String ID of the vehicle.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE vehicles
               SET is_available = 1
             WHERE vehicle_id = ?;
        """, (vehicle_id,))
        self.conn.commit()


# Quick smoke test when run directly
if __name__ == "__main__":
    ms = MaintenanceScheduler()
    print("Scheduling maintenance (threshold 10 000 km)...")
    events = ms.schedule_maintenance()
    if events:
        print("Maintenance events created:")
        for e in events:
            print(e)
    else:
        print("No vehicles needed maintenance.")

    print("\nFull maintenance log:")
    for entry in ms.view_log():
        print(entry)

    # Example: mark one vehicle available again
    if events:
        vid = events[0]["vehicle_id"]
        print(f"\nCompleting maintenance for {vid}...")
        ms.complete_maintenance(vid)
        print(f"{vid} is now available.")
