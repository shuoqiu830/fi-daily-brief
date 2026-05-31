"""
Fetches financial headlines via RSS feeds.
RSS is reliable and not blocked unlike direct page scraping.
"""

import requests
import xml.etree.ElementTree as ET
from config import MAX_HEADLINES_PER_SOURCE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FIBriefBot/1.0)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

TIMEOUT = 10

# RSS feeds — reliable, not paywalled
RSS_SOURCES = [
    {
        "name": "CNBC: Economy",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258",
    },
    {
        "name": "CNBC: Bonds",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839135",
    },
    {
        "name": "CNBC: World Economy",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    },
    {
        "name": "Bloomberg: Economy",
        "url": "https://feeds.bloomberg.com/economics/news.rss",
    },
    {
        "name": "Bloomberg: Markets",
        "url": "https://feeds.bloomberg.com/markets/news.rss",
    },
    {
        "name": "WSJ: Markets",
        "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    },
    {
        "name": "WSJ: World News",
        "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    },
    {
        "name": "WSJ: US Business",
        "url": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
    },
    {
        "name": "Federal Reserve: Press Releases",
        "url": "https://www.federalreserve.gov/feeds/press_all.xml",
    },
]

# FT HTML scrape as fallback supplement (often works when RSS doesn't)
FT_SCRAPE = {
    "name": "FT Markets",
    "url": "https://www.ft.com/markets",
    "headline_selector": "a.js-teaser-heading-link",
}


def parse_rss(xml_text: str, max_items: int) -> list[str]:
    """Extract <title> elements from an RSS feed XML string."""
    headlines = []
    try:
        root = ET.fromstring(xml_text)
        ns = ""
        # Handle both RSS 2.0 and Atom
        for item in root.iter("item"):
            title_el = item.find("title")
            if title_el is not None and title_el.text:
                text = title_el.text.strip()
                if len(text) > 10:
                    headlines.append(text)
            if len(headlines) >= max_items:
                break
        # Atom fallback
        if not headlines:
            atom_ns = "http://www.w3.org/2005/Atom"
            for entry in root.iter(f"{{{atom_ns}}}entry"):
                title_el = entry.find(f"{{{atom_ns}}}title")
                if title_el is not None and title_el.text:
                    headlines.append(title_el.text.strip())
                if len(headlines) >= max_items:
                    break
    except ET.ParseError:
        pass
    return headlines


def fetch_rss_source(source: dict) -> list[str]:
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        headlines = parse_rss(resp.text, MAX_HEADLINES_PER_SOURCE)
        return headlines
    except Exception as e:
        print(f"  [warn] {source['name']}: {e}")
        return []


def _scrape_ft_html() -> list[str]:
    """Supplemental FT HTML scrape."""
    headlines = []
    try:
        resp = requests.get(
            FT_SCRAPE["url"],
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        seen = set()
        for el in soup.select(FT_SCRAPE["headline_selector"]):
            text = el.get_text(strip=True)
            if text and len(text) > 15 and text not in seen:
                headlines.append(text)
                seen.add(text)
            if len(headlines) >= MAX_HEADLINES_PER_SOURCE:
                break
    except Exception as e:
        print(f"  [warn] FT HTML scrape: {e}")
    return headlines


def fetch_all_headlines() -> str:
    """
    Fetches headlines from all RSS sources + FT HTML.
    Returns a formatted text block for the Claude prompt.
    """
    print("Fetching news headlines (RSS)...")
    all_sections = []

    for source in RSS_SOURCES:
        headlines = fetch_rss_source(source)
        if headlines:
            block = f"\n--- {source['name']} ---\n"
            block += "\n".join(f"- {h}" for h in headlines)
            all_sections.append(block)
            print(f"  {source['name']}: {len(headlines)} headlines")
        else:
            print(f"  {source['name']}: unavailable")

    # Supplement with FT HTML
    ft_headlines = _scrape_ft_html()
    if ft_headlines:
        block = f"\n--- {FT_SCRAPE['name']} ---\n"
        block += "\n".join(f"- {h}" for h in ft_headlines)
        all_sections.append(block)
        print(f"  {FT_SCRAPE['name']}: {len(ft_headlines)} headlines")

    if not all_sections:
        return "News feeds unavailable today. Base analysis on market data only."

    return "\n".join(all_sections)


if __name__ == "__main__":
    print(fetch_all_headlines())
