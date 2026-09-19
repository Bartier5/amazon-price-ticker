# main.py
import asyncio
import os
import sys
from auth import save_session
from tracker import run_tracker

SESSION_PATH = os.path.join(
    os.path.dirname(__file__), "session", "amazon_session.json"
)


def session_exists():
    """Check if a saved session file exists."""
    return os.path.exists(SESSION_PATH)


def print_banner():
    print("""
╔═══════════════════════════════════════════╗
║        Amazon Price Tracker v1.0          ║
║   Concurrent · Session-Sharing · Async   ║
╚═══════════════════════════════════════════╝
    """)


async def main():
    print_banner()

    # ── Step 1: Check for saved session ──────────────────────────────────────
    if not session_exists():
        print("⚠️  No saved session found.")
        print("🔐 Launching browser for manual Amazon login...\n")
        await save_session()
    else:
        print("✅ Session found — skipping login.\n")

    # ── Step 2: Run the tracker ───────────────────────────────────────────────
    print("🚀 Starting price tracker...\n")
    await run_tracker()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Tracker stopped manually.")
        sys.exit(0)