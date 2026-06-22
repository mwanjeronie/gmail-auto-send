"""
One-time Gmail login using a real browser window.

Run this script once to log in to Gmail. Your session (cookies) is saved to
session.json so that browser_send.py can reuse it without asking you to log in again.

Usage:
    python3 login.py

Steps:
1. A browser window opens at gmail.com (visible on your screen).
2. Log in with your Google account as you normally would (including 2FA if enabled).
3. Once you can see your Gmail inbox, the script detects it automatically and
   saves the session. The browser closes on its own — you do not need to do anything else.
"""

import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SESSION_FILE = Path("session.json")

# Allow the browser to show on screen when a display is available.
# On Linux this sets the X11 display; on other OS it is ignored.
_DISPLAY = os.environ.get("DISPLAY", ":1")


def main() -> None:
    print(f"Opening browser on display {_DISPLAY} — please log in to Gmail.")
    print("The session will be saved automatically once your inbox is detected.\n")

    env = os.environ.copy()
    env["DISPLAY"] = _DISPLAY
    # Propagate the updated display so the Playwright subprocess picks it up.
    os.environ["DISPLAY"] = _DISPLAY

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ],
            env=env,
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

        print("Waiting for you to log in (up to 3 minutes)...")
        try:
            # Wait until we land on the Gmail inbox (URL contains /mail/u/)
            page.wait_for_url("**/mail/u/**", timeout=180_000)
            # Give Gmail a moment to fully load so all auth cookies are set
            page.wait_for_timeout(3_000)
            print("Inbox detected!")
        except PlaywrightTimeout:
            print(
                "Timed out waiting for login. "
                "Saving whatever session state is available."
            )

        context.storage_state(path=str(SESSION_FILE))
        browser.close()

    print(f"\nSession saved to {SESSION_FILE}.")
    print("You can now send emails with:  python3 browser_send.py --to ... --subject ... --body ...")



if __name__ == "__main__":
    main()
