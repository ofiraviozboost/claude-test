#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Permit Search Script for Hof HaSharon Local Committee
Searches for building permits in Reshpon that match specific criteria
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs


class PermitSearcher:
    """Automates the process of searching and filtering building permits"""

    def __init__(self, base_url: str = "https://vaada.hof-hasharon.co.il"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Status filters - looking for completed permits
        self.target_statuses = ["הושלם", "היתר", "טופס 4"]

        # Keywords to search for in permit details
        self.keywords = ["פל״ח", "בריכה", "פלח"]

        # Area threshold - main area + service area
        self.area_threshold = 320

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_permits_from_page(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract permit information from search results page"""
        permits = []

        # Find the results table
        table = soup.find('table', {'class': 'table'}) or soup.find('table')
        if not table:
            print("Could not find results table")
            return permits

        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3:
                continue

            # Extract permit data
            permit_data = {
                'row_element': row,
                'columns': [col.get_text(strip=True) for col in cols]
            }

            # Look for status in the row
            status_text = ' '.join(permit_data['columns'])

            # Check if status matches our criteria
            if any(status in status_text for status in self.target_statuses):
                # Find the link to permit details
                link = row.find('a', href=True)
                if link:
                    permit_data['details_url'] = urljoin(self.base_url, link['href'])
                    permit_data['permit_number'] = link.get_text(strip=True)
                    permits.append(permit_data)

        return permits

    def get_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """Find the URL for the next page of results"""
        # Look for pagination links
        pagination = soup.find('ul', {'class': 'pagination'}) or soup.find('div', {'class': 'pagination'})

        if pagination:
            next_link = pagination.find('a', string=re.compile(r'הבא|›|Next', re.IGNORECASE))
            if next_link and next_link.get('href'):
                return urljoin(self.base_url, next_link['href'])

        # Alternative: try to increment page number in URL
        parsed = urlparse(current_url)
        params = parse_qs(parsed.query)
        if 'page' in params:
            current_page = int(params['page'][0])
            next_page = current_page + 1
            # Try to construct next page URL
            next_url = current_url.replace(f'page={current_page}', f'page={next_page}')
            return next_url

        return None

    def check_permit_details(self, details_url: str) -> Optional[Dict]:
        """
        Check permit details for keywords and area criteria
        Returns owner information if criteria are met
        """
        print(f"  Checking: {details_url}")
        soup = self.fetch_page(details_url)
        if not soup:
            return None

        # Get all text content
        page_text = soup.get_text()

        # Check for keywords
        keyword_found = any(keyword in page_text for keyword in self.keywords)

        # Check for area criteria (שטח עיקרי + שרות > 320)
        area_match = False

        # Look for area information
        # Common patterns: "שטח עיקרי: 200", "שטח שרות: 150"
        main_area_pattern = r'שטח\s+עיקרי[:\s]+(\d+(?:\.\d+)?)'
        service_area_pattern = r'שטח\s+שרות[:\s]+(\d+(?:\.\d+)?)'

        main_areas = re.findall(main_area_pattern, page_text)
        service_areas = re.findall(service_area_pattern, page_text)

        if main_areas or service_areas:
            main_area = float(main_areas[0]) if main_areas else 0
            service_area = float(service_areas[0]) if service_areas else 0
            total_area = main_area + service_area

            if total_area > self.area_threshold:
                area_match = True
                print(f"    Area match: Main={main_area}, Service={service_area}, Total={total_area}")

        # If either keyword or area criteria is met, extract owner info
        if keyword_found or area_match:
            result = {
                'url': details_url,
                'keyword_found': keyword_found,
                'area_match': area_match,
                'owners': []
            }

            if keyword_found:
                print(f"    ✓ Keyword found!")

            # Try to find owner information
            # Method 1: Look for "בעלי עניין" tab/section
            owners_section = soup.find(string=re.compile(r'בעלי?\s+עניין'))
            if owners_section:
                # Find the parent container
                container = owners_section.find_parent(['div', 'section', 'table'])
                if container:
                    # Extract names (typically in bold or specific structure)
                    names = container.find_all(['strong', 'b'])
                    for name in names:
                        name_text = name.get_text(strip=True)
                        if name_text and len(name_text) > 2:
                            result['owners'].append(name_text)

            # Method 2: Look for common patterns like "שם: ..." or "בעל הנכס: ..."
            owner_patterns = [
                r'בעל\s+(?:ה)?נכס[:\s]+([^\n]+)',
                r'בעל\s+עניין[:\s]+([^\n]+)',
                r'שם[:\s]+([^\n]+)',
            ]

            for pattern in owner_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    owner_name = match.strip()
                    if owner_name and len(owner_name) > 2 and owner_name not in result['owners']:
                        result['owners'].append(owner_name)

            if result['owners']:
                print(f"    ✓ Found owners: {', '.join(result['owners'])}")
                return result
            else:
                print(f"    ⚠ Criteria met but no owner information found")
                return result

        return None

    def search_all_pages(self, start_url: str) -> List[Dict]:
        """
        Search through all pages starting from the given URL
        Returns list of matching permits with owner information
        """
        results = []
        current_url = start_url
        page_num = 1

        while current_url:
            print(f"\nProcessing page {page_num}: {current_url}")
            soup = self.fetch_page(current_url)

            if not soup:
                break

            # Extract permits from current page
            permits = self.extract_permits_from_page(soup)
            print(f"Found {len(permits)} matching permits on this page")

            # Check each permit
            for permit in permits:
                try:
                    permit_info = self.check_permit_details(permit['details_url'])
                    if permit_info:
                        permit_info['permit_number'] = permit.get('permit_number', 'Unknown')
                        results.append(permit_info)
                        print(f"  ✓✓ Match found for permit {permit_info['permit_number']}")

                    # Be nice to the server
                    time.sleep(1)
                except Exception as e:
                    print(f"  Error processing permit: {e}")
                    continue

            # Try to find next page
            next_url = self.get_next_page_url(soup, current_url)

            # Also check if we manually need to construct next page
            if not next_url or next_url == current_url:
                # Try incrementing page number
                if f'page={page_num}' in current_url:
                    next_url = current_url.replace(f'page={page_num}', f'page={page_num + 1}')
                    # Verify the next page exists
                    test_soup = self.fetch_page(next_url)
                    if not test_soup or not self.extract_permits_from_page(test_soup):
                        next_url = None
                else:
                    next_url = None

            current_url = next_url
            page_num += 1

            # Safety limit
            if page_num > 100:
                print("Reached page limit (100), stopping")
                break

            time.sleep(2)  # Be nice to the server between pages

        return results


def main():
    """Main entry point"""
    # URL for Reshpon (מושב רשפון) - Place ID 247
    # This should be the first page URL
    base_search_url = "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/?searchType=ByAddress&AddressPlace=247&page=1"

    print("=" * 80)
    print("Automated Permit Search - Hof HaSharon - Moshav Reshpon")
    print("=" * 80)
    print(f"\nSearching for permits with:")
    print("  - Status: הושלם/היתר/טופס 4")
    print("  - Keywords: פל״ח, בריכה")
    print("  - OR Area (main + service) > 320 sqm")
    print("\n" + "=" * 80 + "\n")

    searcher = PermitSearcher()
    results = searcher.search_all_pages(base_search_url)

    print("\n" + "=" * 80)
    print(f"SEARCH COMPLETE - Found {len(results)} matching permits")
    print("=" * 80 + "\n")

    if results:
        for i, result in enumerate(results, 1):
            print(f"{i}. Permit: {result.get('permit_number', 'Unknown')}")
            print(f"   URL: {result['url']}")
            print(f"   Keyword found: {result['keyword_found']}")
            print(f"   Area criteria met: {result['area_match']}")
            if result['owners']:
                print(f"   Owners: {', '.join(result['owners'])}")
            else:
                print(f"   Owners: Not found")
            print()

        # Save results to JSON file
        output_file = 'permit_search_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Results saved to: {output_file}")
    else:
        print("No matching permits found.")


if __name__ == "__main__":
    main()
