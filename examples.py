"""
Runnable examples that demonstrate how to use gmail.py as a library.

Run after completing the OAuth setup described in README.md:
    python examples.py
"""

from gmail import send_email


def example_plain_text() -> None:
    send_email(
        to=["recipient@example.com"],
        subject="Hello from Gmail Automation",
        body="This is a plain-text email sent via the Gmail API.",
    )


def example_html() -> None:
    html_body = """
    <html>
      <body>
        <h2>Monthly Report</h2>
        <p>Everything is running <strong>smoothly</strong>.</p>
        <ul>
          <li>Tasks completed: 42</li>
          <li>Errors: 0</li>
        </ul>
      </body>
    </html>
    """
    send_email(
        to=["recipient@example.com"],
        subject="Monthly Report",
        body=html_body,
        html=True,
    )


def example_with_cc_and_attachment() -> None:
    send_email(
        to=["alice@example.com"],
        cc=["bob@example.com"],
        subject="Q2 Summary",
        body="Please find the Q2 report attached.",
        attachments=["report.pdf"],  # must exist on disk
    )


def example_bulk_send() -> None:
    """Send a personalised email to each recipient in a list."""
    recipients = [
        {"email": "alice@example.com", "name": "Alice"},
        {"email": "bob@example.com", "name": "Bob"},
    ]
    for person in recipients:
        send_email(
            to=[person["email"]],
            subject=f"Hi {person['name']}!",
            body=f"Dear {person['name']},\n\nThank you for your interest!\n\nBest regards",
        )


if __name__ == "__main__":
    # Change this to call whichever example you want to try.
    example_plain_text()
