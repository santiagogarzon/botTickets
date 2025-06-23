# Flight Price Watcher

This application periodically checks for flight prices on LEVEL's website for a specific route and date range. If it finds a price below a certain threshold, it sends a notification via Telegram.

## Features

- **Scheduled Execution**: Runs automatically every 2 minutes.
- **API Polling**: Fetches flight data from the LEVEL API.
- **Database Storage**: Saves all found flight prices in a SQLite database.
- **Telegram Notifications**: Alerts you when a cheap flight is found.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**

    - Rename `.env.example` to `.env`.
    - Open the `.env` file and add your Telegram Bot Token and your Chat ID.

    ```ini
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"
    # Optional: for currency conversion
    # EXCHANGERATE_API_KEY="YOUR_API_KEY"
    ```

    To get your `TELEGRAM_CHAT_ID`, you can message the `@userinfobot` on Telegram. To create a bot and get a token, talk to `@BotFather`.

4.  **Run the application:**
    ```bash
    python main.py
    ```
# botTickets
