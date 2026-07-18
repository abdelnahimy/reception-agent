import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reception.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create resources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            description TEXT
        )
    """)
    
    # 2. Create bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            duration_hours INTEGER NOT NULL,
            resource_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            FOREIGN KEY (resource_name) REFERENCES resources (name)
        )
    """)
    
    # 3. Create faq table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    """)
    
    # 4. Create chat_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    # Seed resources if empty
    cursor.execute("SELECT COUNT(*) FROM resources")
    if cursor.fetchone()[0] == 0:
        resources = [
            ("Meeting Room A", "Room", 6, "Equipped with a whiteboard and 4K screen. Best for small team syncs."),
            ("Meeting Room B", "Room", 8, "Spacious room with videoconference system and projector."),
            ("Conference Room", "Room", 15, "Large room for board meetings, presentations, and town halls."),
            ("Lunch Table 1", "Table", 4, "Window-side table in the dining hall."),
            ("Lunch Table 2", "Table", 2, "Quiet corner table in the dining hall.")
        ]
        cursor.executemany("INSERT INTO resources (name, type, capacity, description) VALUES (?, ?, ?, ?)", resources)
        
    # Seed FAQ if empty
    cursor.execute("SELECT COUNT(*) FROM faq")
    if cursor.fetchone()[0] == 0:
        faqs = [
            ("reception hours, opening hours, schedule", "Our reception is open from 8:00 AM to 6:00 PM, Monday through Friday."),
            ("wifi, internet, password", "Guest Wi-Fi is available. Network name: 'Guest-WiFi', password: 'WelcomeToReception2026'."),
            ("parking, car park, visitor parking", "Free visitor parking is available at the front of the building. Visitor spaces are clearly marked with a green 'V'."),
            ("phone, contact, email, phone number", "You can contact the reception at +1-555-0199 or via email at reception@company.com."),
            ("address, location, direction", "We are located at 100 Innovation Way, Tech Park, Suite 100, on the ground floor.")
        ]
        cursor.executemany("INSERT INTO faq (question, answer) VALUES (?, ?)", faqs)

    # Seed some sample bookings if empty
    cursor.execute("SELECT COUNT(*) FROM bookings")
    if cursor.fetchone()[0] == 0:
        today_str = date.today().isoformat()
        sample_bookings = [
            ("John Doe", today_str, "10:00", 2, "Meeting Room A", "active", datetime.now().isoformat()),
            ("Jane Smith", today_str, "14:00", 1, "Conference Room", "active", datetime.now().isoformat()),
            ("Bob Johnson", today_str, "12:00", 1, "Lunch Table 1", "cancelled", datetime.now().isoformat()),
            ("Alice Williams", today_str, "15:30", 2, "Meeting Room B", "active", datetime.now().isoformat())
        ]
        cursor.executemany("INSERT INTO bookings (guest_name, date, time, duration_hours, resource_name, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", sample_bookings)
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
