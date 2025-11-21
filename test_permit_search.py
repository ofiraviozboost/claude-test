#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script - runs on first page only
"""

import sys
sys.path.insert(0, '/home/user/claude-test')

from permit_search import PermitSearcher


def main():
    """Test with first page only"""
    base_search_url = "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/?searchType=ByAddress&AddressPlace=247&page=1"

    print("=" * 80)
    print("QUICK TEST - First Page Only")
    print("=" * 80)

    searcher = PermitSearcher()

    # Fetch first page
    soup = searcher.fetch_page(base_search_url)
    if not soup:
        print("Failed to fetch page")
        return

    # Extract permits
    permits = searcher.extract_permits_from_page(soup)
    print(f"\nFound {len(permits)} permits with matching status on first page")

    # Test with first 2 permits only
    test_count = min(2, len(permits))
    print(f"Testing first {test_count} permits...\n")

    for i, permit in enumerate(permits[:test_count], 1):
        print(f"\n{i}. Testing permit: {permit.get('permit_number', 'Unknown')}")
        print(f"   URL: {permit['details_url']}")

        result = searcher.check_permit_details(permit['details_url'])
        if result:
            print(f"   ✓ MATCH FOUND!")
            print(f"   Owners: {', '.join(result['owners']) if result['owners'] else 'Not found'}")
        else:
            print(f"   No match")

    print("\n" + "=" * 80)
    print("Test complete. To run full search, use: python3 permit_search.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
