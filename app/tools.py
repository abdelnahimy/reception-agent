import sqlite3
import os
from datetime import datetime, date
from google.adk.tools import ToolContext
from app.database import get_db_connection

def parse_time(t_str: str) -> float:
    try:
        h, m = map(int, t_str.split(':'))
        return h + m / 60.0
    except Exception:
        return 0.0

def check_overlap(t1: str, dur1: int, t2: str, dur2: int) -> bool:
    start1 = parse_time(t1)
    end1 = start1 + dur1
    start2 = parse_time(t2)
    end2 = start2 + dur2
    return max(start1, start2) < min(end1, end2)

def list_bookings() -> dict:
    """List all current bookings in the database with their details.

    Returns:
        A dictionary containing the status of the operation and a list of all bookings.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, guest_name, date, time, duration_hours, resource_name, status, created_at FROM bookings ORDER BY date ASC, time ASC")
        rows = cursor.fetchall()
        bookings = [dict(r) for r in rows]
        conn.close()
        return {"status": "success", "bookings": bookings}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_availability(resource_name: str, date_str: str, time_str: str, duration_hours: int) -> dict:
    """Check if a specific room or table is available at the requested date and time.

    Args:
        resource_name: The name of the room or table (e.g., 'Meeting Room A', 'Lunch Table 1').
        date_str: The booking date in YYYY-MM-DD format.
        time_str: The booking start time in HH:MM format (24-hour clock).
        duration_hours: The duration of the booking in hours (usually 1 or 2).

    Returns:
        A dictionary indicating if the resource is available, with details or suggestions.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Verify resource exists
        cursor.execute("SELECT name FROM resources WHERE name = ?", (resource_name,))
        if not cursor.fetchone():
            cursor.execute("SELECT name FROM resources")
            resources = [r[0] for r in cursor.fetchall()]
            conn.close()
            return {
                "status": "error",
                "available": False,
                "message": f"Resource '{resource_name}' does not exist. Available resources are: {', '.join(resources)}."
            }
            
        # 2. Get active bookings for that resource and date
        cursor.execute(
            "SELECT id, time, duration_hours FROM bookings WHERE resource_name = ? AND date = ? AND status = 'active'",
            (resource_name, date_str)
        )
        bookings = cursor.fetchall()
        conn.close()
        
        # Check overlaps
        for b in bookings:
            b_time = b["time"]
            b_dur = b["duration_hours"]
            if check_overlap(time_str, duration_hours, b_time, b_dur):
                return {
                    "status": "success",
                    "available": False,
                    "message": f"'{resource_name}' is occupied at that time due to an existing booking from {b_time} (duration: {b_dur}h)."
                }
                
        return {
            "status": "success",
            "available": True,
            "message": f"'{resource_name}' is available on {date_str} at {time_str} for {duration_hours} hour(s)."
        }
    except Exception as e:
        return {"status": "error", "available": False, "message": str(e)}

def create_booking(guest_name: str, resource_name: str, date_str: str, time_str: str, duration_hours: int) -> dict:
    """Create a new room or table booking in the system.

    Args:
        guest_name: The full name of the guest booking the resource.
        resource_name: The name of the resource (e.g., 'Meeting Room A', 'Lunch Table 1').
        date_str: The booking date in YYYY-MM-DD format.
        time_str: The booking start time in HH:MM format (24-hour clock).
        duration_hours: The duration of the booking in hours (usually 1 or 2).

    Returns:
        A dictionary with the result of the booking creation.
    """
    try:
        # 1. Date and time validation
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = date.today()
        if booking_date < today:
            return {"status": "error", "message": "Cannot create bookings in the past."}
            
        # Business hours check (8:00 AM to 6:00 PM)
        start_hour = parse_time(time_str)
        if start_hour < 8.0 or (start_hour + duration_hours) > 18.0:
            return {"status": "error", "message": "Bookings must be within reception business hours (08:00 AM to 06:00 PM)."}
            
        # 2. Check availability
        avail_res = check_availability(resource_name, date_str, time_str, duration_hours)
        if not avail_res.get("available"):
            return {"status": "error", "message": avail_res.get("message")}
            
        # 3. Create booking
        conn = get_db_connection()
        cursor = conn.cursor()
        created_at = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO bookings (guest_name, date, time, duration_hours, resource_name, status, created_at) VALUES (?, ?, ?, ?, ?, 'active', ?)",
            (guest_name, date_str, time_str, duration_hours, resource_name, created_at)
        )
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": f"Successfully created booking (ID: {booking_id}) for {guest_name} on {date_str} at {time_str} for {duration_hours} hour(s) in '{resource_name}'."
        }
    except ValueError:
        return {"status": "error", "message": "Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cancel_booking(booking_id: int) -> dict:
    """Cancel an existing booking using its booking ID.

    Args:
        booking_id: The integer ID of the booking to cancel.

    Returns:
        A dictionary containing the status of the cancellation.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if booking exists
        cursor.execute("SELECT id, guest_name, status FROM bookings WHERE id = ?", (booking_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"status": "error", "message": f"Booking ID {booking_id} not found."}
            
        if row["status"] == "cancelled":
            conn.close()
            return {"status": "success", "message": f"Booking ID {booking_id} is already cancelled."}
            
        # Update status
        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": f"Successfully cancelled booking ID {booking_id} for {row['guest_name']}."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def answer_faq(query: str) -> dict:
    """Retrieve answers for reception frequently asked questions (FAQs) such as hours, Wi-Fi, location, contact, and parking.

    Args:
        query: The search query, keywords, or question.

    Returns:
        A dictionary containing the answers or a mismatch message.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM faq")
        faqs = cursor.fetchall()
        conn.close()
        
        query_lower = query.lower()
        best_match = None
        for faq in faqs:
            keywords = [kw.strip() for kw in faq["question"].split(",")]
            for kw in keywords:
                if kw in query_lower:
                    best_match = faq["answer"]
                    break
            if best_match:
                break
                
        if best_match:
            return {"status": "success", "answer": best_match}
        else:
            return {
                "status": "not_found",
                "message": "I couldn't find an exact match for that FAQ. Our standard FAQs cover Wi-Fi password, opening hours, visitor parking, office address, and contact details."
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
