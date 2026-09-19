# tracker.py
import asyncio
from playwright.async_api import async_playwright
from auth import load_session_into_context
from scraper import scrape_price
from notifier import notify
from config import PRODUCTS, NUM_CONTEXTS, CURRENCY


def split_into_batches(products, num_batches):
    """
    Split a flat list of products into num_batches roughly equal chunks.

    Example:
        10 products, 2 batches → [[p1,p2,p3,p4,p5], [p6,p7,p8,p9,p10]]

    math.ceil ensures no products are left out when the list
    doesn't divide evenly — e.g. 11 products / 3 contexts:
        batch_size = ceil(11/3) = 4
        batches → [4, 4, 3]  ← last batch gets the remainder
    """
    import math
    batch_size = math.ceil(len(products) / num_batches)
    return [
        products[i * batch_size : (i + 1) * batch_size]
        for i in range(num_batches)
        if products[i * batch_size : (i + 1) * batch_size]
        # ↑ filter out empty batches when products < num_batches
    ]


async def run_context(browser, context_id, product_batch):
    """
    One context's full lifecycle:
    - Create context
    - Load session (appears logged in)
    - Loop through assigned products
    - Scrape each price
    - Compare and notify
    - Close context when done
    """
    print(f"\n🚀 Context {context_id} starting — "
          f"{len(product_batch)} products assigned")

    # Create a fresh isolated browser context
    context = await browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    )

    # Inject the saved Amazon session into this context
    # All 10 contexts call this — all appear as the same logged-in user
    await load_session_into_context(context)

    # Open one tab inside this context
    page = await context.new_page()

    # Loop through this context's assigned products sequentially
    for product in product_batch:
        name = product["name"]
        url = product["url"]
        target = product["target_price"]

        print(f"\n  [{context_id}] 🔍 Checking: {name}")

        current_price = await scrape_price(page, url)

        if current_price is not None:
            print(f"  [{context_id}] 💰 Price  : {CURRENCY}{current_price:,.2f}")
            print(f"  [{context_id}] 🎯 Target : {CURRENCY}{target:,.2f}")

            if current_price <= target:
                print(f"  [{context_id}] ✅ ALERT: {name} dropped below target!")
                # Trigger notification — we'll build this in checkpoint 5
                await notify(name, url, current_price, target)
            else:
                diff = current_price - target
                print(f"  [{context_id}] 📈 {CURRENCY}{diff:,.2f} above target.")
        else:
            print(f"  [{context_id}] ⚠️  Could not retrieve price for {name}")

        # Small delay between products within the same context
        # Avoids hammering Amazon with back-to-back requests
        await asyncio.sleep(2)

    # Always close the context when done — frees memory
    await context.close()
    print(f"\n✅ Context {context_id} finished.")


async def run_tracker():
    """
    Main coordinator:
    - Splits products into batches
    - Launches one browser
    - Fires all contexts simultaneously via asyncio.gather()
    """
    print(f"🎯 Starting tracker — {len(PRODUCTS)} products "
          f"across {NUM_CONTEXTS} contexts\n")

    # Split all products into batches — one batch per context
    batches = split_into_batches(PRODUCTS, NUM_CONTEXTS)

    print("📦 Batch assignments:")
    for i, batch in enumerate(batches, 1):
        names = [p["name"] for p in batch]
        print(f"  Context {i}: {names}")

    async with async_playwright() as p:

        # ONE browser shared across all contexts
        # headless=True — no visible window needed
        browser = await p.chromium.launch(headless=True)

        # Build the list of coroutines — one per context
        # Each coroutine is a run_context() call waiting to fire
        tasks = [
            run_context(browser, context_id=i + 1, product_batch=batch)
            for i, batch in enumerate(batches)
        ]

        # THIS is the magic line —
        # asyncio.gather() launches ALL tasks simultaneously
        # and waits for every single one to finish before continuing
        await asyncio.gather(*tasks)

        await browser.close()

    print("\n🏁 All contexts finished. Tracker complete.")


if __name__ == "__main__":
    asyncio.run(run_tracker())