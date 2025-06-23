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
                found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
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

if __name__ == '__main__':
    # This allows creating the database manually by running `python database.py`
    init_db() 