# notifier.py — placeholder until checkpoint 5
async def notify(name, url, current_price, target_price):
    print(f"  🔔 [NOTIFY] {name} — Price: ₦{current_price:,.2f} "
          f"(target: ₦{target_price:,.2f}) | {url}")