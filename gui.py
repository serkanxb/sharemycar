#!/usr/bin/env python3
# gui.py

import tkinter as tk  # Core GUI library
from tkinter import ttk, messagebox  # Themed widgets (Notebook, Treeview, etc.)

# Import our backend managers
from database import initialize_database, get_db_path

from vehicle_manager import VehicleManager
from booking_manager import BookingManager
from return_manager import ReturnManager
from maintenance_scheduler import MaintenanceScheduler
from transaction_manager import TransactionManager
from financial_manager import FinancialManager


class ShareMyCarApp(tk.Tk):
    """
    Main application window for ShareMyCar GUI.
    Creates a tabbed interface and wires up all operations.
    """

    def __init__(self):
        """
        Initialize the main window, managers, and all tabs.
        """

        # Create or open the DB & tables before doing anything else
        initialize_database(get_db_path())

        super().__init__()  # Initialize parent tk.Tk (with parentheses!)
        # Initialize parent tk.Tk
        self.title("ShareMyCar Management")  # Window title
        self.geometry("800x600")  # Default window size

        # Instantiate backend managers
        self.vm = VehicleManager()
        self.bm = BookingManager()
        self.rm = ReturnManager()
        self.ms = MaintenanceScheduler()
        self.tm = TransactionManager()
        self.fm = FinancialManager()

        # Create the Notebook (tab container)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Build each tab
        self._build_inventory_tab()
        self._build_booking_tab()
        self._build_return_tab()
        self._build_maintenance_tab()
        self._build_transaction_tab()
        self._build_financial_tab()

    def _build_inventory_tab(self):
        """
        Sets up the 'Inventory' tab: view current vehicles + add new ones.
        """
        frame = ttk.Frame(self.notebook)  # Container for inventory widgets
        self.notebook.add(frame, text="Inventory")

        # --- Vehicle list ---
        lbl = ttk.Label(frame, text="Fleet Inventory:")
        lbl.pack(pady=5)

        # Treeview to display vehicles in columns
        cols = ("ID", "Brand/Model", "Mileage", "€ /day", "€ /km", "Available")
        self.inv_tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for c in cols:
            self.inv_tree.heading(c, text=c)
        self.inv_tree.pack(fill="x", padx=10)

        # Load initial data
        self._refresh_inventory()

        # --- Add new vehicle ---
        sep = ttk.Separator(frame, orient="horizontal")
        sep.pack(fill="x", pady=10)

        form = ttk.Frame(frame)
        form.pack(pady=5)

        # --- Add New Vehicle Form ---
        add_frame = ttk.LabelFrame(frame, text="Add New Vehicle")
        add_frame.pack(fill="x", padx=10, pady=10)

        # Row 0: Brand & Model      | Mileage
        ttk.Label(add_frame, text="Brand & Model").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_bm = ttk.Entry(add_frame, width=25)
        self.new_bm.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(add_frame, text="Mileage (km)").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.new_mil = ttk.Entry(add_frame, width=10)
        self.new_mil.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Row 1: Daily Price         | Maint Cost
        ttk.Label(add_frame, text="Daily Price (€)").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.new_price = ttk.Entry(add_frame, width=10)
        self.new_price.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(add_frame, text="Maint Cost (€ /km)").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.new_maint = ttk.Entry(add_frame, width=10)
        self.new_maint.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Row 2: Add Button
        ttk.Button(add_frame, text="Add Vehicle", command=self._add_vehicle) \
            .grid(row=2, column=3, padx=5, pady=10, sticky="e")

    def _refresh_inventory(self):
        """
        Clear and reload the inventory Treeview from the database.
        """
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)  # Remove existing rows
        for v in self.vm.view_inventory():  # Fetch fresh data
            avail = "Yes" if v["is_available"] else "No"
            self.inv_tree.insert("", "end", values=(
                v["vehicle_id"],
                v["brand_model"],
                v["mileage"],
                f"{v['daily_price']:.2f}",
                f"{v['maint_cost_per_km']:.2f}",
                avail
            ))

    def _add_vehicle(self):
        """
        Handler for the 'Add Vehicle' button.
        Reads form entries, adds to DB, and refreshes the list.
        """
        # 1) Auto‑generate
        vid = self.vm.generate_vehicle_id()
        messagebox.showinfo("Generated ID", f"Assigned Vehicle ID: {vid}")

        # 2) Read the rest of the form
        bm = self.new_bm.get().strip()
        mil = int(self.new_mil.get().strip())
        price = float(self.new_price.get().strip())
        maint = float(self.new_maint.get().strip())

        # 3) Add & refresh
        self.vm.add_vehicle(vid, bm, mil, price, maint)
        self._refresh_inventory()

        # 4) Clear the form for next input
        self.new_bm.delete(0, tk.END)
        self.new_mil.delete(0, tk.END)
        self.new_price.delete(0, tk.END)
        self.new_maint.delete(0, tk.END)

    def _build_booking_tab(self):
        """
        Sets up the 'Bookings' tab:
          - A grouped form to create new bookings
          - A table to view existing bookings
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Bookings")

        # --- New Booking Form ---
        form_frame = ttk.LabelFrame(frame, text="Create New Booking")
        form_frame.pack(fill="x", padx=10, pady=10)

        # Row 0: Customer & Vehicle ID
        ttk.Label(form_frame, text="Customer").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.b_cust = ttk.Entry(form_frame, width=20)
        self.b_cust.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Vehicle ID").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.b_vid = ttk.Entry(form_frame, width=10)
        self.b_vid.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Row 1: Start Date & Duration
        ttk.Label(form_frame, text="Start Date (YYYY-MM‑DD)").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.b_start = ttk.Entry(form_frame, width=15)
        self.b_start.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Duration (days)").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.b_days = ttk.Entry(form_frame, width=5)
        self.b_days.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Row 2: Estimated km & Submit button
        ttk.Label(form_frame, text="Est. km").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.b_estkm = ttk.Entry(form_frame, width=10)
        self.b_estkm.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        create_btn = ttk.Button(form_frame, text="Create Booking", command=self._create_booking)
        create_btn.grid(row=2, column=3, padx=5, pady=5, sticky="e")

        # --- Existing Bookings List ---
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("ID", "Customer", "Vehicle", "Start", "End", "Est km", "Est cost")
        self.book_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=6)
        for c in cols:
            self.book_tree.heading(c, text=c)
            self.book_tree.column(c, anchor="center")
        self.book_tree.pack(fill="both", expand=True)

        self._refresh_bookings()

    def _create_booking(self):
        """
        Handler to create a booking from form data and refresh the list.
        """
        cust = self.b_cust.get().strip()
        vid = self.b_vid.get().strip()
        start = self.b_start.get().strip()
        days = int(self.b_days.get().strip())
        km = int(self.b_estkm.get().strip())

        try:
            b = self.bm.create_booking(cust, vid, start, days, km)  # Backend call
        except Exception as e:
            tk.messagebox.showerror("Booking Error", str(e))  # Show any error
            return
        self._refresh_inventory()  # Vehicle availability may have changed
        self._refresh_bookings()  # Show new booking

        # Clear booking form
        self.b_cust.delete(0, tk.END)
        self.b_vid.delete(0, tk.END)
        self.b_start.delete(0, tk.END)
        self.b_days.delete(0, tk.END)
        self.b_estkm.delete(0, tk.END)

    def _refresh_bookings(self):
        """
        Reload the bookings Treeview from the database.
        """
        for i in self.book_tree.get_children():
            self.book_tree.delete(i)
        for b in self.bm.view_bookings():
            self.book_tree.insert("", "end", values=(
                b["booking_id"],
                b["customer_name"],
                b["vehicle_id"],
                b["start_date"],
                b["end_date"],
                b["est_km"],
                f"{b['est_cost']:.2f}"
            ))

    def _build_return_tab(self):
        """
        Sets up the 'Returns' tab: process returns and view past returns.
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Returns")

        # Form for return
        form = ttk.Frame(frame)
        form.pack(pady=10)
        ttk.Label(form, text="Booking ID").grid(row=0, column=0, sticky="e")
        self.r_bid = ttk.Entry(form)
        self.r_bid.grid(row=0, column=1, padx=5)
        ttk.Label(form, text="Actual km").grid(row=0, column=2, sticky="e")
        self.r_km = ttk.Entry(form)
        self.r_km.grid(row=0, column=3, padx=5)
        ttk.Label(form, text="Return date").grid(row=1, column=0, sticky="e")
        self.r_date = ttk.Entry(form)
        self.r_date.grid(row=1, column=1, padx=5)
        ttk.Button(form, text="Process Return", command=self._process_return) \
            .grid(row=1, column=3, pady=5)

        # Treeview for past returns
        cols = ("Return ID", "Booking ID", "km", "Late", "Clean", "Maint", "Date")
        self.ret_tree = ttk.Treeview(frame, columns=cols, show="headings", height=6)
        for c in cols: self.ret_tree.heading(c, text=c)
        self.ret_tree.pack(fill="x", padx=10, pady=10)
        self._refresh_returns()

    def _process_return(self):
        """
        Handler to process a return and refresh inventory/bookings/returns.
        """
        bid = int(self.r_bid.get().strip())
        km = int(self.r_km.get().strip())
        date = self.r_date.get().strip()
        try:
            self.rm.process_return(bid, km, date)  # Backend call
        except Exception as e:
            tk.messagebox.showerror("Return Error", str(e))
            return
        self._refresh_inventory()
        self._refresh_bookings()
        self._refresh_returns()

        # Yenile: envanter, rezervasyonlar, iadeler
        self._refresh_inventory()
        self._refresh_bookings()
        self._refresh_returns()
        # Yeni ekleme: işlemler ve finansal raporu da yenile
        self._refresh_transactions()
        self._refresh_financial_report()

        # Formu temizle
        self.r_bid.delete(0, tk.END)
        self.r_km.delete(0, tk.END)
        self.r_date.delete(0, tk.END)

    def _refresh_returns(self):
        """
        Reload the returns Treeview from the database.
        """
        for i in self.ret_tree.get_children():
            self.ret_tree.delete(i)
        for r in self.rm.view_returns():
            self.ret_tree.insert("", "end", values=(
                r["return_id"],
                r["booking_id"],
                r["actual_km"],
                f"{r['late_fee']:.2f}",
                f"{r['clean_fee']:.2f}",
                f"{r['maint_cost']:.2f}",
                r["return_date"]
            ))

    def _build_maintenance_tab(self):
        """
        Sets up the 'Maintenance' tab: schedule and view maintenance log.
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Maintenance")

        # Button to run scheduling
        ttk.Button(frame, text="Check & Schedule", command=self._schedule_maint) \
            .pack(pady=10)
        # Treeview for maintenance log
        cols = ("ID", "Vehicle", "Mileage", "Cost", "Date")
        self.maint_tree = ttk.Treeview(frame, columns=cols, show="headings", height=6)
        for c in cols: self.maint_tree.heading(c, text=c)
        self.maint_tree.pack(fill="x", padx=10, pady=10)
        self._refresh_maintenance()

    def _schedule_maint(self):
        """
        Handler to run maintenance scheduling and refresh displays.
        """
        self.ms.schedule_maintenance()
        self._refresh_inventory()
        self._refresh_maintenance()

    def _refresh_maintenance(self):
        """
        Reload the maintenance log Treeview.
        """
        for i in self.maint_tree.get_children():
            self.maint_tree.delete(i)
        for m in self.ms.view_log():
            self.maint_tree.insert("", "end", values=(
                m["maint_id"],
                m["vehicle_id"],
                m["mileage_at_maint"],
                f"{m['cost']:.2f}",
                m["date"]
            ))

    def _build_transaction_tab(self):
        """
        Sets up the 'Transactions' tab: view all logged transactions.
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Transactions")

        cols = ("ID", "Customer", "Vehicle", "Days", "Rev", "Clean", "Maint", "Late", "Date")
        self.tx_tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for c in cols: self.tx_tree.heading(c, text=c)
        self.tx_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self._refresh_transactions()

    def _refresh_transactions(self):
        """
        Reload the transactions Treeview.
        """
        for i in self.tx_tree.get_children():
            self.tx_tree.delete(i)
        for t in self.tm.view_transactions():
            self.tx_tree.insert("", "end", values=(
                t["trans_id"],
                t["customer_name"],
                t["vehicle_id"],
                t["rental_duration"],
                f"{t['revenue']:.2f}",
                f"{t['cleaning_fee']:.2f}",
                f"{t['maintenance_fee']:.2f}",
                f"{t['late_fee']:.2f}",
                t["date"]
            ))

    def _build_financial_tab(self):
        """
        Sets up the 'Financials' tab: show key metrics.
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Financial Report")

        # Finansal metrikleri hesapla
        rpt = self.fm.generate_full_report()

        # Label’ları saklayalım ki güncelleyebilelim
        self.fin_rev_lbl = ttk.Label(frame, text=f"Total Revenue: €{rpt['total_revenue']:.2f}")
        self.fin_rev_lbl.pack(pady=5)
        self.fin_cost_lbl = ttk.Label(frame, text=f"Total Costs:   €{rpt['total_operational_costs']:.2f}")
        self.fin_cost_lbl.pack(pady=5)
        self.fin_prof_lbl = ttk.Label(frame, text=f"Total Profit:  €{rpt['total_profit']:.2f}")
        self.fin_prof_lbl.pack(pady=5)
        self.fin_avg_lbl = ttk.Label(frame, text=f"Avg. Mileage:  {rpt['average_mileage']:.2f} km")
        self.fin_avg_lbl.pack(pady=5)

    def _refresh_financial_report(self):
        """
        Finansal sekmedeki metrikleri güncelle.
        """
        rpt = self.fm.generate_full_report()
        self.fin_rev_lbl.config(text=f"Total Revenue: €{rpt['total_revenue']:.2f}")
        self.fin_cost_lbl.config(text=f"Total Costs:   €{rpt['total_operational_costs']:.2f}")
        self.fin_prof_lbl.config(text=f"Total Profit:  €{rpt['total_profit']:.2f}")
        self.fin_avg_lbl.config(text=f"Avg. Mileage:  {rpt['average_mileage']:.2f} km")


if __name__ == "__main__":
    app = ShareMyCarApp()  # Instantiate the GUI application
    app.mainloop()  # Enter the Tk event loop
