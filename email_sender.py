"""
Sends the daily brief as a formatted HTML email via Gmail SMTP.
"""

import os
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


# ── HTML styling ──────────────────────────────────────────────────────────────

CSS = """
    body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px;
           color: #1a1a2e; background: #f5f5f5; margin: 0; padding: 20px; }
    .container { max-width: 760px; margin: 0 auto; background: #ffffff;
                 border-radius: 6px; overflow: hidden;
                 box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .header { background: #1a237e; color: #ffffff; padding: 20px 28px; }
    .header h1 { margin: 0; font-size: 20px; letter-spacing: 0.5px; }
    .header .date { margin: 4px 0 0; font-size: 13px; color: #c5cae9; }
    .body { padding: 24px 28px; }
    h2 { color: #1a237e; font-size: 14px; text-transform: uppercase;
         letter-spacing: 0.8px; border-bottom: 2px solid #e8eaf6;
         padding-bottom: 6px; margin-top: 24px; margin-bottom: 10px; }
    h2:first-child { margin-top: 0; }
    p { margin: 6px 0; line-height: 1.6; }
    ul { margin: 6px 0; padding-left: 20px; }
    li { margin: 4px 0; line-height: 1.6; }
    .footer { background: #f5f5f5; padding: 12px 28px;
              font-size: 11px; color: #9e9e9e; text-align: center; }
    strong { color: #283593; }
"""


def markdown_to_html(text: str) -> str:
    """
    Lightweight Markdown-to-HTML for the brief text.
    Handles: ## headings, **bold**, bullet lists, and paragraphs.
    """
    lines = text.split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Section headers (## or numbered like "1. EXECUTIVE SUMMARY")
        if stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{stripped[3:].strip()}</h2>")

        elif re.match(r"^\d+\.\s+[A-Z]", stripped):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            title = re.sub(r"^\d+\.\s+", "", stripped)
            html_lines.append(f"<h2>{title}</h2>")

        # Bullet points
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = stripped[2:]
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
            html_lines.append(f"<li>{content}</li>")

        # Sub-bullets
        elif stripped.startswith("   - ") or stripped.startswith("  - "):
            content = stripped.lstrip("- ").strip()
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
            html_lines.append(f"<li style='margin-left:16px'>{content}</li>")

        # Blank line
        elif not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("")

        # Normal paragraph line
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            html_lines.append(f"<p>{content}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def build_html_email(brief_text: str) -> str:
    date_str = datetime.now().strftime("%A, %B %d, %Y")
    body_html = markdown_to_html(brief_text)

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>{CSS}</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Fixed Income Daily Brief</h1>
      <div class="date">{date_str}</div>
    </div>
    <div class="body">
      {body_html}
    </div>
    <div class="footer">
      Generated automatically | Market data via Yahoo Finance | Analysis by Claude AI
    </div>
  </div>
</body>
</html>"""


def send_email(brief_text: str):
    """Send the brief as a formatted HTML email via Gmail SMTP."""
    gmail_user = os.environ["GMAIL_USER"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    recipients_raw = os.environ.get("EMAIL_RECIPIENTS", gmail_user)
    recipients = [r.strip() for r in recipients_raw.split(",")]

    date_str = datetime.now().strftime("%b %d, %Y")
    subject = f"FI Daily Brief - {date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = ", ".join(recipients)

    html_content = build_html_email(brief_text)
    msg.attach(MIMEText(brief_text, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    print(f"Sending email to {recipients}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipients, msg.as_string())

    print("Email sent.")


if __name__ == "__main__":
    # Preview HTML locally without sending
    sample = """## EXECUTIVE SUMMARY
- **10Y Treasury yields** rose 8 bps to 4.52% as hotter-than-expected CPI data pushed rate cut expectations further out.
- **Credit spreads** widened modestly; HYG fell 0.4% on risk-off sentiment.
- **DXY** strengthened 0.6% to 105.2, weighing on EM debt.

## US RATES
The Treasury curve bear-flattened intraday after the CPI print...
"""
    html = build_html_email(sample)
    with open("preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Preview saved to preview.html - open in a browser to review.")
