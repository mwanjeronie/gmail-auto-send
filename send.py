"""
Command-line interface for sending Gmail messages.

Usage examples
--------------
# Basic email
python send.py --to friend@example.com --subject "Hello" --body "Hi there!"

# HTML email
python send.py --to a@example.com --subject "Report" --body "<h1>Done</h1>" --html

# Multiple recipients with CC and attachment
python send.py \\
    --to a@example.com b@example.com \\
    --cc boss@example.com \\
    --subject "Q2 Report" \\
    --body "See attached." \\
    --attach report.pdf notes.txt
"""

import argparse
import sys

from gmail import send_email


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send an email from your Gmail account via the Gmail API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--to",
        nargs="+",
        required=True,
        metavar="ADDRESS",
        help="One or more recipient email addresses.",
    )
    parser.add_argument(
        "--subject",
        required=True,
        help="Email subject line.",
    )
    parser.add_argument(
        "--body",
        required=True,
        help="Email body (plain text or HTML).",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        default=False,
        help="Treat --body as HTML rather than plain text.",
    )
    parser.add_argument(
        "--cc",
        nargs="+",
        default=None,
        metavar="ADDRESS",
        help="CC recipients.",
    )
    parser.add_argument(
        "--bcc",
        nargs="+",
        default=None,
        metavar="ADDRESS",
        help="BCC recipients.",
    )
    parser.add_argument(
        "--attach",
        nargs="+",
        default=None,
        metavar="FILE",
        help="One or more file paths to attach.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    send_email(
        to=args.to,
        subject=args.subject,
        body=args.body,
        html=args.html,
        cc=args.cc,
        bcc=args.bcc,
        attachments=args.attach,
    )


if __name__ == "__main__":
    main()
