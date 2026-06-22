"""
Core email sending logic using the Gmail API.

Supports:
- Plain-text and HTML bodies
- File attachments
- Multiple recipients (to, cc, bcc)
"""

import base64
import mimetypes
import os
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth import get_credentials


def _build_message(
    sender: str,
    to: list[str],
    subject: str,
    body: str,
    html: bool = False,
    cc: Optional[list[str]] = None,
    bcc: Optional[list[str]] = None,
    attachments: Optional[list[str]] = None,
) -> dict:
    """Construct a MIME message and encode it for the Gmail API."""
    if attachments:
        msg = MIMEMultipart("mixed")
        body_part = MIMEMultipart("alternative")
        body_part.attach(MIMEText(body, "html" if html else "plain"))
        msg.attach(body_part)

        for filepath in attachments:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"Attachment not found: {filepath}")
            mime_type, _ = mimetypes.guess_type(str(path))
            main_type, sub_type = (mime_type or "application/octet-stream").split("/", 1)
            with path.open("rb") as f:
                part = MIMEBase(main_type, sub_type)
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition", "attachment", filename=path.name
                )
                msg.attach(part)
    else:
        msg = MIMEText(body, "html" if html else "plain")

    msg["From"] = sender
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = ", ".join(cc)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)

    encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": encoded}


def send_email(
    to: list[str],
    subject: str,
    body: str,
    html: bool = False,
    cc: Optional[list[str]] = None,
    bcc: Optional[list[str]] = None,
    attachments: Optional[list[str]] = None,
    sender: str = "me",
) -> dict:
    """
    Send an email via the Gmail API.

    Args:
        to:          List of recipient email addresses.
        subject:     Email subject line.
        body:        Plain-text or HTML body.
        html:        Set True when body contains HTML.
        cc:          Optional CC recipients.
        bcc:         Optional BCC recipients.
        attachments: Optional list of file paths to attach.
        sender:      Gmail address to send from (defaults to 'me', the authenticated account).

    Returns:
        The API response dict containing the sent message id.

    Raises:
        HttpError: If the Gmail API returns an error.
    """
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    message = _build_message(
        sender=sender,
        to=to,
        subject=subject,
        body=body,
        html=html,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
    )

    try:
        result = (
            service.users()
            .messages()
            .send(userId="me", body=message)
            .execute()
        )
        print(f"Email sent successfully. Message ID: {result['id']}")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise
