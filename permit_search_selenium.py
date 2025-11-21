#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Permit Search Script using Selenium
This version opens a real browser and allows manual CAPTCHA solving
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


class PermitSearcherSelenium:
    """Automates permit search using Selenium WebDriver"""

    def __init__(self, headless: bool = False):
        """
        Initialize Selenium WebDriver

        Args:
            headless: If True, runs without GUI. Set to False to solve CAPTCHA manually.
        """
        self.target_statuses = ["הושלם", "היתר", "טופס 4"]
        self.keywords = ["פל״ח", "בריכה", "פלח"]
        self.area_threshold = 320

        # Setup Chrome options
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
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            print("\nTrying Firefox...")
            try:
                self.driver = webdriver.Firefox()
                self.wait = WebDriverWait(self.driver, 20)
            except Exception as e2:
                print(f"Error initializing Firefox driver: {e2}")
                raise Exception("Could not initialize any browser driver. Please install Chrome/Firefox driver.")

    def solve_captcha_manually(self, timeout: int = 60):
        """
        Wait for user to solve CAPTCHA manually

        Args:
            timeout: Maximum time to wait for CAPTCHA solution (seconds)
        """
        print("\n" + "=" * 80)
        print("⚠ CAPTCHA DETECTED")
        print("=" * 80)
        print(f"Please solve the CAPTCHA in the browser window within {timeout} seconds...")
        print("The script will continue automatically once solved.")
        print("=" * 80 + "\n")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check if we've moved past the CAPTCHA (results table visible)
                table = self.driver.find_element(By.TAG_NAME, 'table')
                if table:
                    print("✓ CAPTCHA solved! Continuing...")
                    return True
            except NoSuchElementException:
                pass

            time.sleep(2)

        print("✗ CAPTCHA timeout reached")
        return False

    def navigate_to_search(self, url: str) -> bool:
        """Navigate to search results page"""
        try:
            print(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(3)

            # Check for CAPTCHA
            page_source = self.driver.page_source
            if 'recaptcha' in page_source.lower() or 'captcha' in page_source.lower():
                if not self.solve_captcha_manually():
                    return False

            return True
        except Exception as e:
            print(f"Error navigating: {e}")
            return False

    def extract_permits_from_page(self) -> List[Dict]:
        """Extract permit information from current page"""
        permits = []

        try:
            # Wait for table to load
            table = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table, table'))
            )

            # Find all rows
            rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip header

            for row in rows:
                try:
                    cols = row.find_elements(By.TAG_NAME, 'td')
                    if len(cols) < 3:
                        continue

                    # Get row text
                    row_text = ' '.join([col.text for col in cols])

                    # Check status
                    if any(status in row_text for status in self.target_statuses):
                        # Find link
                        links = row.find_elements(By.TAG_NAME, 'a')
                        if links:
                            permit_data = {
                                'permit_number': links[0].text.strip(),
                                'details_url': links[0].get_attribute('href'),
                                'status': row_text
                            }
                            permits.append(permit_data)

                except Exception as e:
                    continue

            print(f"Found {len(permits)} matching permits on this page")
            return permits

        except TimeoutException:
            print("Timeout waiting for table to load")
            return []

    def check_permit_details(self, permit_data: Dict) -> Optional[Dict]:
        """Check permit details in a new tab"""
        print(f"  Checking permit: {permit_data['permit_number']}")

        # Open link in new tab
        original_window = self.driver.current_window_handle
        self.driver.execute_script(f"window.open('{permit_data['details_url']}', '_blank');")

        # Switch to new tab
        self.driver.switch_to.window(self.driver.window_handles[-1])

        try:
            # Wait for page to load
            time.sleep(2)

            # Get page text
            page_text = self.driver.page_source

            # Check for keywords
            keyword_found = any(keyword in page_text for keyword in self.keywords)

            # Check for area
            area_match = False
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

            if keyword_found or area_match:
                result = {
                    'permit_number': permit_data['permit_number'],
                    'url': permit_data['details_url'],
                    'keyword_found': keyword_found,
                    'area_match': area_match,
                    'owners': []
                }

                if keyword_found:
                    print(f"    ✓ Keyword found!")

                # Try to extract owner information
                # Look for "בעלי עניין" tab
                try:
                    owner_tabs = self.driver.find_elements(
                        By.XPATH,
                        "//*[contains(text(), 'בעל') and contains(text(), 'עניין')]"
                    )
                    if owner_tabs:
                        owner_tabs[0].click()
                        time.sleep(1)

                        # Get updated page text
                        page_text = self.driver.page_source

                except Exception:
                    pass

                # Extract owner names
                owner_patterns = [
                    r'בעל\s+(?:ה)?נכס[:\s]+([^\n<]+)',
                    r'בעל\s+עניין[:\s]+([^\n<]+)',
                    r'שם[:\s]+([^\n<]+)',
                ]

                for pattern in owner_patterns:
                    matches = re.findall(pattern, page_text)
                    for match in matches:
                        owner_name = match.strip()
                        if owner_name and len(owner_name) > 2 and owner_name not in result['owners']:
                            # Clean HTML tags
                            owner_name = re.sub(r'<[^>]+>', '', owner_name)
                            if owner_name and len(owner_name) > 2:
                                result['owners'].append(owner_name)

                if result['owners']:
                    print(f"    ✓ Found owners: {', '.join(result['owners'])}")
                else:
                    print(f"    ⚠ Criteria met but no owner information found")

                return result

            return None

        finally:
            # Close tab and switch back
            self.driver.close()
            self.driver.switch_to.window(original_window)

    def get_next_page_number(self) -> Optional[int]:
        """Get next page number from pagination"""
        try:
            # Look for "next" button or page numbers
            pagination = self.driver.find_elements(By.CSS_SELECTOR, '.pagination a, .pager a')

            for link in pagination:
                text = link.text.strip()
                if 'הבא' in text or '›' in text or 'Next' in text.lower():
                    href = link.get_attribute('href')
                    if href:
                        # Extract page number
                        match = re.search(r'page=(\d+)', href)
                        if match:
                            return int(match.group(1))

            # Try to get current page and increment
            current_url = self.driver.current_url
            match = re.search(r'page=(\d+)', current_url)
            if match:
                current_page = int(match.group(1))
                return current_page + 1

            return None

        except Exception as e:
            print(f"Error getting next page: {e}")
            return None

    def search_all_pages(self, start_url: str, max_pages: int = 100) -> List[Dict]:
        """Search through all pages"""
        results = []

        if not self.navigate_to_search(start_url):
            print("Failed to navigate to search page")
            return results

        page_num = 1

        while page_num <= max_pages:
            print(f"\n{'=' * 80}")
            print(f"Processing page {page_num}")
            print('=' * 80)

            # Extract permits from current page
            permits = self.extract_permits_from_page()

            if not permits:
                print("No more permits found, ending search")
                break

            # Check each permit
            for permit in permits:
                try:
                    result = self.check_permit_details(permit)
                    if result:
                        results.append(result)
                        print(f"  ✓✓ Match found for permit {result['permit_number']}")

                    time.sleep(1)  # Be nice to the server

                except Exception as e:
                    print(f"  Error processing permit: {e}")
                    continue

            # Try to go to next page
            next_page = self.get_next_page_number()
            if not next_page:
                print("No more pages found")
                break

            # Navigate to next page
            current_url = self.driver.current_url
            next_url = re.sub(r'page=\d+', f'page={next_page}', current_url)

            print(f"\nNavigating to page {next_page}...")
            self.driver.get(next_url)
            time.sleep(2)

            page_num = next_page

        return results

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()


def main():
    """Main entry point"""
    base_search_url = "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/?searchType=ByAddress&AddressPlace=247&page=1"

    print("=" * 80)
    print("Automated Permit Search - Selenium Version")
    print("Hof HaSharon - Moshav Reshpon")
    print("=" * 80)
    print(f"\nSearching for permits with:")
    print("  - Status: הושלם/היתר/טופס 4")
    print("  - Keywords: פל״ח, בריכה")
    print("  - OR Area (main + service) > 320 sqm")
    print("\n" + "=" * 80)
    print("\nℹ A browser window will open. If CAPTCHA appears, please solve it manually.")
    print("=" * 80 + "\n")

    searcher = None

    try:
        # headless=False allows manual CAPTCHA solving
        searcher = PermitSearcherSelenium(headless=False)
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

            # Save results
            output_file = 'permit_search_results_selenium.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Results saved to: {output_file}")
        else:
            print("No matching permits found.")

    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if searcher:
            print("\nClosing browser...")
            searcher.close()


if __name__ == "__main__":
    main()
