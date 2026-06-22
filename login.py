"""
One-time Gmail login using a real browser window.

Run this script once to log in to Gmail. Your session (cookies) is saved to
session.json so that browser_send.py can reuse it without asking you to log in again.

Usage:
    python3 login.py

Steps:
1. A visible Chrome window opens at gmail.com.
2. Log in with your Google account as you normally would (including 2FA if enabled).
3. Once you see your Gmail inbox, press ENTER in this terminal.
4. The session is saved to session.json and the browser closes.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_FILE = Path("session.json")


def main() -> None:
    print("Opening browser — log in to Gmail, then come back here and press ENTER.")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"],
        )
        context = browser.new_context(
            viewport=None,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.goto("https://mail.google.com/")

        try:
            input("\nPress ENTER once you are logged in and can see your Gmail inbox > ")
        except EOFError:
            print("Non-interactive mode detected — waiting 120 s for manual login.")
            page.wait_for_timeout(120_000)

        context.storage_state(path=str(SESSION_FILE))
        browser.close()

    print(f"\nSession saved to {SESSION_FILE}. You can now run browser_send.py.")


if __name__ == "__main__":
    main()
