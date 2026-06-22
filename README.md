# gmail-auto-send

Send emails from your Gmail account programmatically using the official Gmail API and OAuth2. Supports plain-text and HTML bodies, CC/BCC, and file attachments.

---

## How it works

Authentication uses OAuth2 (the same standard Google uses for "Sign in with Google"). You authorize the app once in your browser; a `token.json` file is saved locally so every subsequent run skips the browser prompt.

No passwords are stored. The token only grants permission to **send mail** (`gmail.send` scope) — it cannot read, delete, or modify any existing messages.

---

## Setup

### 1. Enable the Gmail API and create OAuth credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Navigate to **APIs & Services → Library**, search for **Gmail API**, and click **Enable**.
4. Navigate to **APIs & Services → OAuth consent screen**:
   - Choose **External** (works for personal accounts).
   - Fill in the required fields (app name, support email).
   - Add your own Gmail address under **Test users**.
5. Navigate to **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Desktop app**.
   - Click **Create**, then **Download JSON**.
6. Rename the downloaded file to `credentials.json` and place it in this project's root directory.

> `credentials.json` and `token.json` are listed in `.gitignore` — **never commit them**.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Authorize (first run only)

```bash
python send.py --to you@example.com --subject "Test" --body "Hello!"
```

A browser window opens asking you to grant permission. After you approve, `token.json` is saved and the email is sent. All future runs skip this step.

---

## Usage

### Command-line

```bash
# Plain-text email
python send.py --to recipient@example.com --subject "Hello" --body "Hi there!"

# HTML email
python send.py \
  --to recipient@example.com \
  --subject "Report" \
  --body "<h1>All done</h1><p>See details below.</p>" \
  --html

# Multiple recipients with CC and an attachment
python send.py \
  --to alice@example.com bob@example.com \
  --cc manager@example.com \
  --subject "Q2 Report" \
  --body "Please find the report attached." \
  --attach report.pdf
```

Full option reference:

| Flag | Description |
|---|---|
| `--to` | One or more recipient addresses (required) |
| `--subject` | Subject line (required) |
| `--body` | Email body — plain text or HTML (required) |
| `--html` | Treat `--body` as HTML |
| `--cc` | CC recipients |
| `--bcc` | BCC recipients |
| `--attach` | One or more file paths to attach |

### Python library

```python
from gmail import send_email

# Plain text
send_email(
    to=["alice@example.com"],
    subject="Hello",
    body="Hi Alice!",
)

# HTML with attachment
send_email(
    to=["alice@example.com"],
    subject="Q2 Report",
    body="<h1>Q2</h1><p>See attachment.</p>",
    html=True,
    attachments=["report.pdf"],
)

# Bulk / personalised sending
recipients = [
    {"email": "alice@example.com", "name": "Alice"},
    {"email": "bob@example.com",   "name": "Bob"},
]
for person in recipients:
    send_email(
        to=[person["email"]],
        subject=f"Hi {person['name']}!",
        body=f"Dear {person['name']}, thanks for reaching out!",
    )
```

See `examples.py` for more patterns.

---

## File structure

```
.
├── auth.py          # OAuth2 flow — get/refresh credentials
├── gmail.py         # Core send_email() function
├── send.py          # CLI entry point
├── examples.py      # Runnable usage examples
├── requirements.txt
├── credentials.json # ← you add this (not committed)
└── token.json       # ← auto-generated after first auth (not committed)
```

---

## Security notes

- Add `credentials.json` and `token.json` to `.gitignore` (see below).
- Never share or commit either file.
- To revoke access at any time, visit [Google Account Permissions](https://myaccount.google.com/permissions) and remove the app.

---

## .gitignore

```
credentials.json
token.json
__pycache__/
*.pyc
.env
```
