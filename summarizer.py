"""
Calls Claude API to generate the daily fixed income narrative.
"""

import os
import anthropic
from datetime import datetime
from config import CLAUDE_MODEL


SYSTEM_PROMPT = """You are a senior fixed income strategist at a major asset management firm.
Your job is to write a concise, professional daily market brief for a fixed income portfolio manager.

Guidelines:
- Lead with the most market-moving macro or geopolitical theme of the day.
- Be precise with numbers: always reference actual yield levels and basis point moves.
- Identify the key driver(s) behind rate moves (e.g., inflation data, central bank commentary, risk-off flows).
- Highlight cross-asset signals that matter for fixed income (USD, oil, equities, VIX).
- Flag any divergence between asset classes (e.g., rates rallying while credit spreads widen).
- Tone: institutional, data-driven, no fluff. Bullet points where appropriate.
- Do not speculate beyond what the data and headlines support.
"""


def build_user_prompt(market_text: str, news_text: str, report_date: str) -> str:
    return f"""Today is {report_date}. Please write the Fixed Income Daily Brief for today.

== MARKET DATA ==
{market_text}

== NEWS HEADLINES ==
{news_text}

== REPORT STRUCTURE ==
Write the brief in the following sections:

1. EXECUTIVE SUMMARY (5-7 bullets covering ALL of the following with actual numbers):
   - The single most important macro or geopolitical theme driving markets today
   - US equity markets: S&P 500, Dow, Nasdaq (levels + % change)
   - European equity markets: Euro Stoxx 50, DAX, FTSE 100 (% change, note if closed)
   - Asian equity markets: Nikkei, Hang Seng, Shanghai Composite (% change)
   - Key commodities: Gold, WTI/Brent crude, and any other notable mover (% change)
   - The dominant fixed income theme of the day (yield moves, spreads, credit)

2. GLOBAL MACRO & GEOPOLITICS
   - Key macro developments (data releases, central bank commentary, geopolitical risk)
   - Implications for fixed income

3. US RATES
   - Treasury curve movement (level + bps change for 2Y, 5Y, 10Y, 30Y)
   - Curve shape dynamics (steepening/flattening, inversion status)
   - Key driver of today's move

4. CREDIT MARKETS
   Cover each of the following asset classes with: (a) price/spread direction, (b) a concise rationale explaining WHY it moved (e.g., macro driver, risk sentiment, rate sensitivity, technicals, supply/demand):
   - **US Investment Grade (LQD):** spread direction + rationale
   - **US High Yield (HYG):** spread direction + rationale
   - **Bank Loans (BKLN):** floating-rate dynamics, CLO demand, leverage sentiment + rationale
   - **Agency MBS (MBB):** prepayment/extension risk, rate vol, spread vs Treasuries + rationale
   - **Private Credit (BIZD as BDC proxy):** note this is an imperfect liquid proxy; comment on middle-market credit conditions, risk appetite for illiquid assets + rationale
   - **EM Debt (EMB/EMHY):** EM risk sentiment, USD/rates impact + rationale
   - Flag any notable divergence between asset classes

5. GLOBAL SOVEREIGNS
   - Key moves in Bunds, Gilts, JGBs, and EM rates
   - Central bank divergence themes

6. INFLATION & TIPS
   - Breakeven dynamics
   - TIPS performance

7. CROSS-ASSET CONTEXT
   - USD, commodities, equities and what they signal for fixed income

8. KEY RISKS & WATCH ITEMS
   - 2-3 items to monitor in the next 24-48 hours

Keep the entire brief under 1200 words. Use a professional, institutional tone.
"""


def generate_brief(market_text: str, news_text: str) -> str:
    """Calls Claude and returns the formatted brief as a string."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    report_date = datetime.now().strftime("%A, %B %d, %Y")

    print("Generating brief with Claude...")
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": build_user_prompt(market_text, news_text, report_date),
            }
        ],
    )

    return message.content[0].text


if __name__ == "__main__":
    # Quick test with dummy data
    from data_fetcher import fetch_all, format_market_data_for_prompt
    from news_scraper import fetch_all_headlines

    market_data = fetch_all()
    market_text = format_market_data_for_prompt(market_data)
    news_text = fetch_all_headlines()
    brief = generate_brief(market_text, news_text)
    print(brief)
