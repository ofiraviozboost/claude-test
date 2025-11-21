#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart automated search - attempts to bypass blocks
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
from typing import List, Dict, Optional


def create_smart_session():
    """Create a session with realistic headers"""
    session = requests.Session()

    # More realistic headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    })

    return session


def test_single_page_access():
    """Test if we can access a single page"""

    url = "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/?searchType=ByAddress&AddressPlace=247&page=1"

    print("🔍 Attempting to access page 1...")
    print(f"URL: {url}")
    print("=" * 80)

    session = create_smart_session()

    try:
        # Try with long timeout
        print("⏳ Sending request (timeout: 60 seconds)...")
        response = session.get(url, timeout=60, allow_redirects=True)

        print(f"✅ Response received!")
        print(f"   Status code: {response.status_code}")
        print(f"   Content length: {len(response.content)} bytes")

        if response.status_code != 200:
            print(f"❌ Bad status code: {response.status_code}")
            return False

        # Check for CAPTCHA
        if 'recaptcha' in response.text.lower():
            print("🧩 CAPTCHA detected in response")
            print("   This means the site requires human verification")
            return False

        # Check for actual content
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='footable')

        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            print(f"✅ Table found with {len(rows)} results!")
            return True
        else:
            print("❌ No results table found in response")
            return False

    except requests.Timeout:
        print("❌ Request timed out (60 seconds)")
        return False

    except requests.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("Smart Search - Testing Site Access")
    print("=" * 80)
    print()

    success = test_single_page_access()

    print()
    print("=" * 80)
    if success:
        print("✅ SUCCESS! Site is accessible")
        print("   We can proceed with automated search")
    else:
        print("❌ FAILED! Site is not accessible from this environment")
        print()
        print("This means:")
        print("  1. The site blocks automated access (bots)")
        print("  2. CAPTCHA is required")
        print("  3. Or the site is temporarily down")
        print()
        print("Solution:")
        print("  Run the script from your local computer using:")
        print("  python3 permit_search_selenium.py")
    print("=" * 80)
