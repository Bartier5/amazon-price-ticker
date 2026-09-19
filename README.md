# Amazon Price Tracker

A concurrent Amazon price tracker built with Python async Playwright.
Monitors multiple products simultaneously and alerts you when prices 
drop below your target.

## Architecture

- Logs into Amazon **once** and saves the session
- Spins up **multiple browser contexts** simultaneously — all sharing 
  the same logged-in identity
- Each context monitors its own batch of products concurrently
- Sends **email alerts** when a price drops below your threshold
- Logs all alerts to a local JSON file

## Tech Stack

- Python 3.8+
- Playwright (async)
- asyncio
- smtplib
- python-dotenv

## Setup

### 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

### 2. Configure environment
cp .env.example .env
# Fill in your Gmail credentials and receiver email

### 3. Add your products
# Edit config.py — add product URLs and target prices

### 4. Run
python main.py

## First Run
On first run, a browser window opens for you to log into Amazon manually.
After login, press Enter — the session is saved and reused on all 
future runs. No password is ever stored.

## Project Structure
amazon-price-tracker/
├── main.py         # Entry point
├── config.py       # Products and settings
├── auth.py         # Session save and load
├── scraper.py      # Single product price scraper
├── tracker.py      # Concurrent multi-context coordinator
├── notifier.py     # Email and file alerts
├── session/        # Saved session and logs (gitignored)
├── .env            # Email credentials (gitignored)
└── requirements.txt