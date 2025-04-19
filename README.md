# ShareMyCar Management System

A standalone Python application to manage a car‑sharing fleet.  
Supports vehicle inventory, bookings, returns, maintenance scheduling, transaction logging, and real‑time financial reporting — all via both a CLI and a Tkinter GUI.

---

## Features

1. **Vehicle Inventory**  
   - View all vehicles  
   - Auto‑generate unique vehicle IDs  
   - Add new vehicles  

2. **Bookings**  
   - Create bookings (customer, dates, estimated km)  
   - Auto‑calculate estimated cost  
   - Mark vehicle as unavailable during rental  

3. **Returns**  
   - Record actual km driven  
   - Calculate late fees (€10/day), cleaning fees (€20), maintenance fees (per‑km)  
   - Update vehicle mileage and availability  

4. **Maintenance Scheduling**  
   - Automatically log maintenance when a vehicle exceeds 10 000 km since last service  
   - View maintenance history  

5. **Transaction Logs**  
   - Log each completed rental with all fees and revenue  
   - View or export transaction history  

6. **Financial Metrics**  
   - Total revenue, total costs, total profit  
   - Average mileage per vehicle  
   - Full financial report  

7. **User Interfaces**  
   - **CLI**: `main.py` menu-driven terminal interface  
   - **GUI**: `gui.py` tabbed Tkinter application  

---

## Requirements

- **Python**: 3.7 or newer  
- **Libraries** (all built‑in):  
  - `sqlite3` (database)  
  - `tkinter` (GUI)  
  - `datetime`  

---

## Installation & Setup

1. **Clone the repo**  
   ```bash
   git clone https://github.com/serkanxb/ShareMyCar.git
   cd ShareMyCar
