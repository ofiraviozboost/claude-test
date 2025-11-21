#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Automated Permit Search
This script automates the entire process of searching and analyzing permits
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import re
from typing import List, Dict, Optional
from datetime import datetime


class FullAutoPermitSearcher:
    """Fully automated permit search with Selenium"""

    def __init__(self, headless: bool = False):
        """Initialize with option to run headless or with GUI"""

        # Configuration
        self.target_statuses = ["הושלם", "היתר", "טופס 4", "החלטה לאשר", "הפקת אגרה"]
        self.keywords = ["פל״ח", "בריכה", "פלח"]
        self.area_threshold = 320

        # Setup Chrome
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            print("✅ Chrome driver initialized")
        except Exception as e:
            print(f"❌ Error initializing Chrome: {e}")
            print("Trying Firefox...")
            try:
                self.driver = webdriver.Firefox()
                self.wait = WebDriverWait(self.driver, 20)
                print("✅ Firefox driver initialized")
            except Exception as e2:
                raise Exception(f"Could not initialize browser: {e2}")

    def wait_for_captcha_if_needed(self):
        """Wait for user to solve CAPTCHA if present"""
        page_source = self.driver.page_source.lower()

        if 'recaptcha' in page_source or 'captcha' in page_source:
            print("\n" + "=" * 80)
            print("🧩 CAPTCHA DETECTED!")
            print("=" * 80)
            print("Please solve the CAPTCHA in the browser window.")
            print("The script will continue automatically once solved...")
            print("=" * 80)

            # Wait for CAPTCHA to be solved (check for table)
            for i in range(60):  # 60 attempts = 2 minutes
                try:
                    table = self.driver.find_element(By.CSS_SELECTOR, 'table.footable, table')
                    if table:
                        print("\n✅ CAPTCHA solved! Continuing...")
                        time.sleep(2)
                        return True
                except:
                    pass
                time.sleep(2)

            print("⚠️ Timeout waiting for CAPTCHA - continuing anyway")

        return True

    def extract_permits_from_current_page(self) -> List[Dict]:
        """Extract permit data from current page"""
        permits = []

        try:
            # Wait for table
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.footable, table')))
            rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip header

            for row in rows:
                try:
                    cols = row.find_elements(By.TAG_NAME, 'td')
                    if len(cols) < 7:
                        continue

                    # Extract data
                    permit_number_elem = cols[0].find_element(By.TAG_NAME, 'strong')
                    permit_number = permit_number_elem.text.strip()

                    # Get details link
                    link = cols[0].find_element(By.TAG_NAME, 'a')
                    details_url = link.get_attribute('href')

                    status = cols[2].text.strip()
                    address = cols[3].text.strip()
                    applicant = cols[5].text.strip()
                    description = cols[6].text.strip()

                    # Check if status matches
                    matches_status = any(target in status for target in self.target_statuses)

                    if matches_status:
                        permit_data = {
                            'permit_number': permit_number,
                            'status': status,
                            'address': address,
                            'applicant': applicant,
                            'description': description,
                            'details_url': details_url,
                        }
                        permits.append(permit_data)

                except Exception as e:
                    continue

            return permits

        except Exception as e:
            print(f"   ⚠️ Error extracting permits: {e}")
            return []

    def analyze_permit_details(self, permit: Dict) -> Optional[Dict]:
        """Analyze a specific permit's details page"""

        print(f"      Analyzing: {permit['permit_number']}")

        # Open in new tab
        original_window = self.driver.current_window_handle
        self.driver.execute_script(f"window.open('{permit['details_url']}', '_blank');")

        try:
            # Switch to new tab
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(2)

            # Get page text
            page_text = self.driver.page_source

            # Check for keywords
            keyword_found = False
            keywords_matched = []
            for keyword in self.keywords:
                if keyword in page_text:
                    keyword_found = True
                    keywords_matched.append(keyword)

            # Check for area
            area_match = False
            main_area = 0
            service_area = 0

            main_area_pattern = r'שטח\s+עיקרי[:\s]+(\d+(?:\.\d+)?)'
            service_area_pattern = r'שטח\s+שרות[:\s]+(\d+(?:\.\d+)?)'

            main_areas = re.findall(main_area_pattern, page_text)
            service_areas = re.findall(service_area_pattern, page_text)

            if main_areas:
                main_area = float(main_areas[0])
            if service_areas:
                service_area = float(service_areas[0])

            total_area = main_area + service_area

            if total_area > self.area_threshold:
                area_match = True

            # If matches criteria, extract owner info
            if keyword_found or area_match:
                result = {
                    **permit,
                    'keyword_found': keyword_found,
                    'keywords_matched': keywords_matched,
                    'area_match': area_match,
                    'main_area': main_area,
                    'service_area': service_area,
                    'total_area': total_area,
                    'owners': []
                }

                # Try to extract owners
                owner_patterns = [
                    r'בעל\s+(?:ה)?נכס[:\s]+([^\n<>"]{3,50})',
                    r'בעל\s+עניין[:\s]+([^\n<>"]{3,50})',
                    r'שם[:\s]+([א-ת\s]{3,50})',
                ]

                for pattern in owner_patterns:
                    matches = re.findall(pattern, page_text)
                    for match in matches:
                        owner = match.strip()
                        owner = re.sub(r'<[^>]+>', '', owner)
                        owner = re.sub(r'\s+', ' ', owner)
                        if owner and len(owner) > 2 and owner not in result['owners']:
                            result['owners'].append(owner)

                if keyword_found:
                    print(f"         ✅ Keywords: {', '.join(keywords_matched)}")
                if area_match:
                    print(f"         ✅ Area: {total_area} sqm (main: {main_area}, service: {service_area})")
                if result['owners']:
                    print(f"         👤 Owners: {', '.join(result['owners'])}")

                return result

            return None

        except Exception as e:
            print(f"         ⚠️ Error: {e}")
            return None

        finally:
            # Close tab and switch back
            self.driver.close()
            self.driver.switch_to.window(original_window)

    def search_pages(self, place_id: str = "247", place_name: str = "רשפון",
                     max_pages: int = 20, start_page: int = 1) -> List[Dict]:
        """
        Search through multiple pages

        Args:
            place_id: Place ID in the system (247 = רשפון)
            place_name: Place name for display
            max_pages: Maximum number of pages to search
            start_page: Starting page number
        """

        results = []
        base_url = "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/"

        print("\n" + "=" * 80)
        print(f"🔍 Starting search for {place_name}")
        print(f"   Pages: {start_page} to {start_page + max_pages - 1}")
        print(f"   Target statuses: {', '.join(self.target_statuses)}")
        print("=" * 80)

        for page_num in range(start_page, start_page + max_pages):
            print(f"\n📄 Page {page_num}/{start_page + max_pages - 1}")
            print("-" * 80)

            # Navigate to page
            url = f"{base_url}?searchType=ByAddress&AddressPlace={place_id}&page={page_num}"

            try:
                self.driver.get(url)
                time.sleep(2)

                # Check for CAPTCHA on first page
                if page_num == start_page:
                    self.wait_for_captcha_if_needed()

                # Extract permits from page
                permits = self.extract_permits_from_current_page()
                print(f"   Found {len(permits)} permits with matching status")

                # Analyze each permit
                for i, permit in enumerate(permits, 1):
                    print(f"   {i}. {permit['permit_number']} - {permit['applicant']}")

                    result = self.analyze_permit_details(permit)
                    if result:
                        results.append(result)
                        print(f"      ✅✅ MATCH! Added to results")
                    else:
                        print(f"      ❌ No match (no keywords/area)")

                    time.sleep(1)  # Be nice to server

                # Wait between pages
                time.sleep(3)

            except Exception as e:
                print(f"   ⚠️ Error on page {page_num}: {e}")
                continue

        return results

    def save_results(self, results: List[Dict], place_name: str):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{place_name}_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Results saved to: {filename}")
        return filename

    def print_summary(self, results: List[Dict]):
        """Print summary of results"""
        print("\n" + "=" * 80)
        print(f"📊 SEARCH COMPLETE - Found {len(results)} matching permits")
        print("=" * 80)

        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['permit_number']}")
                print(f"   Status: {result['status']}")
                print(f"   Address: {result['address']}")
                print(f"   Applicant: {result['applicant']}")
                if result['keyword_found']:
                    print(f"   ✅ Keywords: {', '.join(result['keywords_matched'])}")
                if result['area_match']:
                    print(f"   ✅ Area: {result['total_area']} sqm")
                if result['owners']:
                    print(f"   👤 Owners: {', '.join(result['owners'])}")
                print(f"   🔗 {result['details_url']}")
        else:
            print("\nNo matching permits found.")

        print("=" * 80)

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()


def main():
    """Main entry point"""

    print("=" * 80)
    print("🤖 FULL AUTOMATED PERMIT SEARCH")
    print("=" * 80)
    print("\nThis script will:")
    print("  1. Search through pages of permits")
    print("  2. Find permits with target statuses")
    print("  3. Check each for keywords (פל״ח, בריכה) or large area (>320 sqm)")
    print("  4. Extract owner information")
    print("  5. Save everything to JSON")
    print("\n" + "=" * 80)

    # Configuration
    PLACES = {
        "רשפון": "247",
        # Add more places here:
        # "כפר שמריהו": "XXX",
        # "הרצליה": "XXX",
    }

    MAX_PAGES_PER_PLACE = 20
    START_PAGE = 1

    # Ask user confirmation
    print(f"\nWill search:")
    for place_name in PLACES.keys():
        print(f"  - {place_name}: pages {START_PAGE}-{START_PAGE + MAX_PAGES_PER_PLACE - 1}")

    print("\nPress Enter to start, or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled by user")
        return

    searcher = None

    try:
        # Initialize searcher (browser will open)
        searcher = FullAutoPermitSearcher(headless=False)

        # Search each place
        all_results = []

        for place_name, place_id in PLACES.items():
            results = searcher.search_pages(
                place_id=place_id,
                place_name=place_name,
                max_pages=MAX_PAGES_PER_PLACE,
                start_page=START_PAGE
            )

            all_results.extend(results)

            # Save intermediate results
            if results:
                searcher.save_results(results, place_name)

        # Print final summary
        searcher.print_summary(all_results)

        # Save combined results
        if all_results:
            filename = searcher.save_results(all_results, "all_places")
            print(f"\n✅ All results saved to: {filename}")

    except KeyboardInterrupt:
        print("\n\n⚠️ Search interrupted by user")

    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if searcher:
            print("\nClosing browser...")
            searcher.close()
            print("✅ Done!")


if __name__ == "__main__":
    main()
