"""
Send Gmail messages by automating the Gmail web interface using a saved browser session.

No API keys or Google Cloud setup required. Just log in once with login.py and
this script handles everything else invisibly in the background.

Usage (CLI):
    python3 browser_send.py --to friend@example.com --subject "Hi" --body "Hello!"

Usage (library):
    from browser_send import browser_send_email
    browser_send_email(to="friend@example.com", subject="Hi", body="Hello!")
"""

import argparse
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SESSION_FILE = Path("session.json")
GMAIL_COMPOSE_URL = "https://mail.google.com/#compose"


def _wait_for_session() -> None:
    if not SESSION_FILE.exists():
        print(
            "session.json not found.\n"
            "Run  python3 login.py  first to log in and save your session."
        )
        sys.exit(1)


def browser_send_email(
    to: str,
    subject: str,
    body: str,
    headless: bool = True,
) -> None:
    """
    Send an email through the Gmail web UI using a saved browser session.

    Args:
        to:       Recipient email address.
        subject:  Email subject line.
        body:     Email body (plain text).
        headless: Run the browser in the background (default True).
                  Set False to watch the browser automate in real time.
    """
    _wait_for_session()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            storage_state=str(SESSION_FILE),
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        # Open Gmail
        page.goto("https://mail.google.com/", wait_until="domcontentloaded")

        # Detect if session has expired (redirected to accounts.google.com)
        if "accounts.google.com" in page.url:
            browser.close()
            print(
                "Your session has expired.\n"
                "Run  python3 login.py  to log in again."
            )
            sys.exit(1)

        # Click the Compose button
        try:
            compose_btn = page.get_by_role("button", name="Compose")
            compose_btn.wait_for(state="visible", timeout=15_000)
            compose_btn.click()
        except PlaywrightTimeout:
            browser.close()
            print(
                "Could not find the Compose button. "
                "Gmail layout may have changed, or your session expired.\n"
                "Try running  python3 login.py  again."
            )
            sys.exit(1)

        # Fill in To field
        to_field = page.get_by_role("combobox", name="To")
        to_field.wait_for(state="visible", timeout=10_000)
        to_field.fill(to)
        to_field.press("Tab")  # confirm the address

        # Fill in Subject
        subject_field = page.get_by_placeholder("Subject")
        subject_field.wait_for(state="visible", timeout=5_000)
        subject_field.fill(subject)

        # Fill in Body
        body_field = page.locator("div[aria-label='Message Body']")
        body_field.wait_for(state="visible", timeout=5_000)
        body_field.fill(body)

        # Send — keyboard shortcut Ctrl+Enter works reliably across Gmail layouts
        body_field.press("Control+Enter")

        # Wait briefly to confirm the compose window closes (send confirmation)
        try:
            page.wait_for_selector(
                "div[aria-label='Message Body']",
                state="hidden",
                timeout=10_000,
            )
            print(f"Email sent to {to}.")
        except PlaywrightTimeout:
            print(
                "Warning: could not confirm the email was sent "
                "(the compose window did not close in time). "
                "Check your Gmail Sent folder."
            )

        browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a Gmail message via the browser (no API keys needed).",
    )
    parser.add_argument("--to", required=True, help="Recipient email address.")
    parser.add_argument("--subject", required=True, help="Subject line.")
    parser.add_argument("--body", required=True, help="Email body (plain text).")
    parser.add_argument(
        "--visible",
        action="store_true",
        default=False,
        help="Show the browser window while sending (useful for debugging).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    browser_send_email(
        to=args.to,
        subject=args.subject,
        body=args.body,
        headless=not args.visible,
    )


if __name__ == "__main__":
    main()
