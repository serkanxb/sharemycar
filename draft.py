return {
        "booking_id":         booking_id,
        "customer_name":      customer_name,
        "vehicle_id":         vehicle_id,
        "return_date":        return_date_str,
        "actual_km":          actual_km,
        "late_days":          late_days,
        "late_fee":           late_fee,
        "cleaning_fee":       clean_fee,
        "maintenance_fee":    maint_fee,
     "total_additional":   late_fee + clean_fee + maint_fee,
         "total_additional":   late_fee + clean_fee + maint_fee,
         "maintenance_scheduled": maintenance_scheduled,
        "revenue":            est_cost,
        "rental_duration":    rental_days
    }