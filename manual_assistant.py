#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual Assistant - Help with manual permit search
This script helps analyze permits you've already opened manually
"""

import json
import re
from typing import Dict, Optional


class PermitAnalyzer:
    """Analyzes permit HTML that you paste"""

    def __init__(self):
        self.keywords = ["פל״ח", "בריכה", "פלח"]
        self.area_threshold = 320

    def analyze_permit_html(self, html_text: str) -> Dict:
        """
        Analyze HTML from a permit details page

        Usage:
        1. Open permit in browser
        2. Right-click → View Page Source (or Ctrl+U)
        3. Copy all the HTML
        4. Paste into permit_html.txt
        5. Run this script
        """
        result = {
            'keyword_found': False,
            'keywords_matched': [],
            'area_match': False,
            'total_area': 0,
            'main_area': 0,
            'service_area': 0,
            'owners': [],
            'matches_criteria': False
        }

        # Check for keywords
        for keyword in self.keywords:
            if keyword in html_text:
                result['keyword_found'] = True
                result['keywords_matched'].append(keyword)

        # Extract areas
        main_area_pattern = r'שטח\s+עיקרי[:\s]+(\d+(?:\.\d+)?)'
        service_area_pattern = r'שטח\s+שרות[:\s]+(\d+(?:\.\d+)?)'

        main_areas = re.findall(main_area_pattern, html_text)
        service_areas = re.findall(service_area_pattern, html_text)

        if main_areas:
            result['main_area'] = float(main_areas[0])
        if service_areas:
            result['service_area'] = float(service_areas[0])

        result['total_area'] = result['main_area'] + result['service_area']

        if result['total_area'] > self.area_threshold:
            result['area_match'] = True

        # Extract owner names
        owner_patterns = [
            r'בעל\s+(?:ה)?נכס[:\s]+([^\n<>"]+)',
            r'בעל\s+עניין[:\s]+([^\n<>"]+)',
            r'שם[:\s]+([א-ת\s]{3,50})',
        ]

        for pattern in owner_patterns:
            matches = re.findall(pattern, html_text)
            for match in matches:
                owner_name = match.strip()
                owner_name = re.sub(r'<[^>]+>', '', owner_name)  # Remove HTML tags
                owner_name = re.sub(r'\s+', ' ', owner_name)  # Normalize whitespace
                if owner_name and len(owner_name) > 2 and owner_name not in result['owners']:
                    result['owners'].append(owner_name)

        # Determine if matches criteria
        result['matches_criteria'] = result['keyword_found'] or result['area_match']

        return result

    def print_analysis(self, result: Dict, permit_number: str = "Unknown"):
        """Print analysis results"""
        print("\n" + "=" * 80)
        print(f"Analysis for Permit: {permit_number}")
        print("=" * 80)

        if result['matches_criteria']:
            print("\n✅ THIS PERMIT MATCHES YOUR CRITERIA!\n")
        else:
            print("\n❌ This permit does not match criteria\n")

        print(f"Keywords found: {result['keyword_found']}")
        if result['keywords_matched']:
            print(f"  Matched: {', '.join(result['keywords_matched'])}")

        print(f"\nArea analysis:")
        print(f"  Main area: {result['main_area']} sqm")
        print(f"  Service area: {result['service_area']} sqm")
        print(f"  Total: {result['total_area']} sqm")
        print(f"  Exceeds threshold ({self.area_threshold}): {result['area_match']}")

        if result['owners']:
            print(f"\nOwners found:")
            for i, owner in enumerate(result['owners'], 1):
                print(f"  {i}. {owner}")
        else:
            print(f"\n⚠ No owner information found")

        print("=" * 80)


def main():
    """Main interactive mode"""
    print("=" * 80)
    print("Manual Permit Analyzer")
    print("=" * 80)
    print("\nThis tool helps you analyze permits you've opened manually.\n")
    print("Instructions:")
    print("1. Open a permit details page in your browser")
    print("2. View the page source (Ctrl+U or right-click → View Source)")
    print("3. Copy ALL the HTML")
    print("4. Save it to 'permit_html.txt' in this directory")
    print("5. Run this script\n")
    print("=" * 80)

    # Try to read from file
    try:
        with open('permit_html.txt', 'r', encoding='utf-8') as f:
            html_content = f.read()

        if not html_content.strip():
            print("\n⚠ permit_html.txt is empty!")
            print("Please paste the HTML content and try again.")
            return

        # Ask for permit number
        permit_number = input("\nEnter permit number (or press Enter to skip): ").strip()
        if not permit_number:
            permit_number = "Unknown"

        # Analyze
        analyzer = PermitAnalyzer()
        result = analyzer.analyze_permit_html(html_content)
        analyzer.print_analysis(result, permit_number)

        # Save results
        result['permit_number'] = permit_number
        output_file = f'permit_analysis_{permit_number.replace("/", "_")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\nResults saved to: {output_file}")

        # Ask if user wants to continue with another
        print("\n" + "=" * 80)
        response = input("\nAnalyze another permit? (y/n): ").strip().lower()
        if response == 'y':
            print("\nPlease update permit_html.txt with the new permit's HTML and run again.")

    except FileNotFoundError:
        print("\n⚠ File 'permit_html.txt' not found!")
        print("\nCreating template file...")

        with open('permit_html.txt', 'w', encoding='utf-8') as f:
            f.write("<!-- Paste the permit HTML here -->\n")
            f.write("<!-- Instructions:\n")
            f.write("1. Open permit page in browser\n")
            f.write("2. Press Ctrl+U (or Cmd+Option+U on Mac)\n")
            f.write("3. Select all (Ctrl+A) and copy (Ctrl+C)\n")
            f.write("4. Paste here, replacing this comment\n")
            f.write("5. Save file\n")
            f.write("6. Run: python3 manual_assistant.py\n")
            f.write("-->\n")

        print("✓ Created permit_html.txt")
        print("Please follow the instructions in the file and run again.")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
