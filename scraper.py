# scraper.py
import asyncio
from playwright.async_api import async_playwright
from auth import load_session_into_context
import os

# ── Constants ────────────────────────────────────────────────────────────────
SESSION_PATH = os.path.join(os.path.dirname(__file__), "session", "amazon_session.json")

# ── Core scraping function ───────────────────────────────────────────────────

async def scrape_price(page, url):
    """
    Given an already-authenticated page, navigate to a product URL
    and return the current price as a float. Returns None if price
    not found.
    """
    # Retry up to 3 times before giving up
    for attempt in range(1, 4):
        try:
            print(f"  ⏳ Attempt {attempt}/3...")

            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            await page.wait_for_selector(
                "span.a-price > span.a-offscreen",
                timeout=20000
            )

            price_element = await page.query_selector(
                "span.a-price > span.a-offscreen"
            )

            if price_element is None:
                print(f"⚠️  Price element not found for: {url}")
                return None

            raw_price = await price_element.inner_text()

            cleaned = raw_price.strip().replace(",", "")
            numeric = ''.join(c for c in cleaned if c.isdigit() or c == ".")
            price = float(numeric)

            return price

        except Exception as e:
            print(f"  ❌ Attempt {attempt} failed: {e}")

            if attempt < 3:
                print(f"  🔄 Retrying in 5 seconds...")
                await asyncio.sleep(5)  # Wait 5 seconds before retrying
            else:
                print(f"  💀 All 3 attempts failed for: {url}")
                return None


async def check_product(url, target_price):
    """
    Full pipeline for a single product:
    - Launch browser
    - Load session
    - Scrape price
    - Compare against target
    """
    async with async_playwright() as p:

        # headless=True — no visible browser needed for scraping
        browser = await p.chromium.launch(headless=True)

        # Create a fresh context — no cookies yet
        context = await browser.new_context(
            # Disguise as a real browser to avoid bot detection
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )

        # Inject saved Amazon session into this context
        # After this line, Amazon thinks this context is logged in
        await load_session_into_context(context)

        # Open a tab inside the context
        page = await context.new_page()

        print(f"\n🔍 Scraping: {url}")

        # Get the current price
        current_price = await scrape_price(page, url)

        if current_price is not None:
            print(f"💰 Current price : ${current_price}")
            print(f"🎯 Target price  : ${target_price}")

            if current_price <= target_price:
                print(f"✅ ALERT: Price dropped below target!")
            else:
                diff = current_price - target_price
                print(f"📈 Still ${diff:.2f} above target.")
        else:
            print("⚠️  Could not retrieve price.")

        await browser.close()


# ── Run directly for testing ─────────────────────────────────────────────────
if __name__ == "__main__":

    # 🔧 Replace this with a real Amazon product URL
    TEST_URL = "https://www.amazon.com/dp/B0GMPN17CC"
    TARGET_PRICE = 50000.00

    asyncio.run(check_product(TEST_URL, TARGET_PRICE))