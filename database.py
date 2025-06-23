import sqlite3
import logging
from config import DB_FILE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_db():
    """Initializes the database and creates the flights table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                outbound_date TEXT NOT NULL,
                return_date TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL,
                found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(outbound_date, return_date, price)
            )
        ''')
        conn.commit()
        cleanup_old_flights()
        conn.close()
        logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")

def save_flight_price(outbound_date, return_date, price, currency):
    """Saves a flight price record to the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO flights (outbound_date, return_date, price, currency)
            VALUES (?, ?, ?, ?)
        ''', (outbound_date, return_date, price, currency))
        conn.commit()
        conn.close()
        logging.info(f"Saved flight: {outbound_date} -> {return_date} for {price} {currency}")
    except sqlite3.Error as e:
        logging.error(f"Failed to save flight price: {e}")


# Function to check if a flight with given parameters already exists
def flight_price_exists(outbound_date, return_date, price):
    """Checks if a flight with the given parameters already exists in the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM flights
            WHERE outbound_date = ? AND return_date = ? AND price = ?
        ''', (outbound_date, return_date, price))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    except sqlite3.Error as e:
        logging.error(f"Database error while checking flight existence: {e}")
        return False

from datetime import datetime

def cleanup_old_flights():
    """Removes flight entries with outbound_date earlier than today."""
    try:
        today = datetime.today().strftime('%Y-%m-%d')
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM flights
            WHERE outbound_date < ?
        ''', (today,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        logging.info(f"Cleaned up {deleted} old flight(s).")
    except sqlite3.Error as e:
        logging.error(f"Failed to clean up old flights: {e}")

if __name__ == '__main__':
    # This allows creating the database manually by running `python database.py`
    init_db() 