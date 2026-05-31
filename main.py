"""
FI Daily Brief - entry point.

Usage:
  python main.py           # fetch data, generate brief, send email
  python main.py --preview # generate brief and save HTML preview (no email)
  python main.py --test    # send a test email with sample content
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project directory
load_dotenv(Path(__file__).parent / ".env")

from data_fetcher import fetch_all, format_market_data_for_prompt
from news_scraper import fetch_all_headlines
from summarizer import generate_brief
from email_sender import send_email, build_html_email


def check_config():
    """Validate required environment variables before running."""
    missing = []
    required = ["ANTHROPIC_API_KEY"]

    for key in required:
        if not os.environ.get(key):
            missing.append(key)

    if "--preview" not in sys.argv and "--test" not in sys.argv:
        for key in ["GMAIL_USER", "GMAIL_APP_PASSWORD"]:
            if not os.environ.get(key) or "your_" in os.environ.get(key, ""):
                missing.append(key)

    if missing:
        print("ERROR: Missing required config in .env:")
        for k in missing:
            print(f"  - {k}")
        print("\nEdit fi_daily_brief/.env to add these values.")
        sys.exit(1)


def run_preview():
    """Generate brief and save as HTML file for review."""
    market_data = fetch_all()
    market_text = format_market_data_for_prompt(market_data)
    news_text = fetch_all_headlines()
    brief = generate_brief(market_text, news_text)

    # Save HTML preview
    html = build_html_email(brief)
    preview_path = Path(__file__).parent / "preview.html"
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Also save plain text
    txt_path = Path(__file__).parent / "preview.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(brief)

    print(f"\nBrief saved to:")
    print(f"  HTML: {preview_path}")
    print(f"  Text: {txt_path}")
    print("\n--- BRIEF PREVIEW ---")
    print(brief[:1500])
    if len(brief) > 1500:
        print(f"\n... [{len(brief) - 1500} more characters - see preview.html]")


def run_send():
    """Full run: fetch, generate, email."""
    market_data = fetch_all()
    market_text = format_market_data_for_prompt(market_data)
    news_text = fetch_all_headlines()
    brief = generate_brief(market_text, news_text)
    send_email(brief)
    print("Done.")


def run_test():
    """Send a test email with a dummy brief to verify email config."""
    from datetime import datetime
    test_brief = f"""## EXECUTIVE SUMMARY
- This is a **test email** from FI Daily Brief.
- Sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
- If you received this, your email configuration is working correctly.

## US RATES
Test data: 10Y Treasury at 4.50% (+5 bps).

## NEXT STEPS
Configure your .env file and run `python main.py` for a live brief.
"""
    send_email(test_brief)


if __name__ == "__main__":
    check_config()

    if "--preview" in sys.argv:
        print("Running in preview mode (no email)...")
        run_preview()
    elif "--test" in sys.argv:
        print("Sending test email...")
        run_test()
    else:
        print("Running full daily brief...")
        run_send()
