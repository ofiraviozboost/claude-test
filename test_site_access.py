#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alternative approach - try to access the site with different methods
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time


def test_site_access():
    """Test different ways to access the site"""

    # Try different URLs
    test_urls = [
        # Main page
        ("Main site", "https://vaada.hof-hasharon.co.il/"),

        # Direct search page (no CAPTCHA token)
        ("Search page base", "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/"),

        # With parameters but no CAPTCHA
        ("Search with params",
         "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/?searchType=ByAddress&AddressPlace=247"),
    ]

    # Setup session with retries
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # Better headers to look more like a real browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })

    results = []

    for name, url in test_urls:
        print(f"\nTesting: {name}")
        print(f"URL: {url}")
        print("-" * 80)

        try:
            # Increase timeout significantly
            response = session.get(url, timeout=60, allow_redirects=True)

            print(f"✓ Status Code: {response.status_code}")
            print(f"✓ Response Size: {len(response.content)} bytes")
            print(f"✓ Content-Type: {response.headers.get('Content-Type', 'N/A')}")

            # Check for CAPTCHA
            if 'recaptcha' in response.text.lower() or 'captcha' in response.text.lower():
                print("⚠ CAPTCHA detected in response")
            else:
                print("✓ No CAPTCHA detected")

            # Check for table (results)
            if '<table' in response.text:
                print("✓ Table found in response")
            else:
                print("⚠ No table found")

            results.append({
                'name': name,
                'url': url,
                'status': response.status_code,
                'success': True,
                'has_captcha': 'recaptcha' in response.text.lower(),
                'has_table': '<table' in response.text
            })

        except requests.Timeout:
            print(f"✗ TIMEOUT (60 seconds)")
            results.append({'name': name, 'url': url, 'success': False, 'error': 'timeout'})

        except requests.RequestException as e:
            print(f"✗ ERROR: {e}")
            results.append({'name': name, 'url': url, 'success': False, 'error': str(e)})

        time.sleep(2)  # Be nice

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    for result in results:
        if result.get('success'):
            status = "✓ SUCCESS"
            if result.get('has_captcha'):
                status += " (but has CAPTCHA)"
            print(f"{status}: {result['name']}")
        else:
            print(f"✗ FAILED ({result.get('error', 'unknown')}): {result['name']}")

    return results


if __name__ == "__main__":
    print("=" * 80)
    print("Testing Site Accessibility")
    print("=" * 80)
    test_site_access()
