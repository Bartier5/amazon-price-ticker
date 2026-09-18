# auth.py
import asyncio
from playwright.async_api import async_playwright
import json
import os

# Path where the session will be saved
SESSION_PATH = "session/amazon_session.json"

async def save_session():
    async with async_playwright() as p:

        # Launch a VISIBLE browser — you need to log in manually
        # headless=False means you can see and interact with the browser
        browser = await p.chromium.launch(headless=False)

        # A context is like a fresh private browser profile
        # No cookies, no history — clean slate
        context = await browser.new_context()

        # A page is a tab inside that context
        page = await context.new_page()

        # Navigate to Amazon login
        await page.goto("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")

        print("\n🌐 Browser opened.")
        print("👉 Log into Amazon manually in the browser window.")
        print("✅ Once you are fully logged in, come back here and press Enter...\n")

        # Pause here — YOU log in, then press Enter
        input()

        # At this point you are logged in
        # storage_state() captures everything — cookies, localStorage, sessionStorage
        # This is the entire logged-in identity in one JSON file
        storage = await context.storage_state()

        # Make sure the session folder exists
        os.makedirs("session", exist_ok=True)

        # Write the session to disk
        with open(SESSION_PATH, "w") as f:
            json.dump(storage, f, indent=2)

        print(f"✅ Session saved to {SESSION_PATH}")

        await browser.close()


async def load_session_into_context(context):
    """
    Load the saved session cookies into an already-created context.
    Call this before navigating to any Amazon page.
    """
    if not os.path.exists(SESSION_PATH):
        raise FileNotFoundError(
            f"No session found at {SESSION_PATH}. Run auth.py first."
        )

    with open(SESSION_PATH, "r") as f:
        storage = json.load(f)

    # Add cookies from the saved session into this context
    await context.add_cookies(storage["cookies"])
    print("✅ Session loaded into context.")


# Run save_session() when this file is executed directly
if __name__ == "__main__":
    asyncio.run(save_session())