#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze HTML page from permit search results
"""

from bs4 import BeautifulSoup
import json


def analyze_page_html(html_file):
    """Analyze permit search results page"""

    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Find the table
    table = soup.find('table', class_='footable')
    if not table:
        print("❌ לא נמצאה טבלת תוצאות")
        return []

    # Get all rows (skip header)
    rows = table.find_all('tr')[1:]

    permits = []
    target_statuses = ["הושלם", "היתר", "טופס 4", "היתר/טופס 4", "החלטה לאשר", "הפקת אגרה"]

    print("=" * 80)
    print(f"ניתוח עמוד - נמצאו {len(rows)} בקשות")
    print("=" * 80)

    for i, row in enumerate(rows, 1):
        cols = row.find_all('td')
        if len(cols) < 7:
            continue

        # Extract data
        permit_number_elem = cols[0].find('strong')
        permit_number = permit_number_elem.get_text(strip=True) if permit_number_elem else "לא ידוע"

        # Get details link
        details_link = cols[0].find('a', href=True)
        details_url = f"https://vaada.hof-hasharon.co.il{details_link['href']}" if details_link else None

        status = cols[2].get_text(strip=True)
        address = cols[3].get_text(strip=True)
        parcel_info = cols[4].get_text(strip=True)
        applicant = cols[5].get_text(strip=True)
        description = cols[6].get_text(strip=True)

        permit_data = {
            'permit_number': permit_number,
            'status': status,
            'address': address,
            'parcel_info': parcel_info,
            'applicant': applicant,
            'description': description,
            'details_url': details_url,
            'matches_status': any(target_status in status for target_status in target_statuses)
        }

        permits.append(permit_data)

        # Print summary
        print(f"\n{i}. {permit_number}")
        print(f"   סטטוס: {status}")
        if permit_data['matches_status']:
            print(f"   ✅ סטטוס מתאים!")
        else:
            print(f"   ❌ סטטוס לא מתאים (מחפשים: הושלם/היתר/טופס 4)")
        print(f"   כתובת: {address}")
        print(f"   מבקש: {applicant}")
        print(f"   תיאור: {description}")
        if details_url:
            print(f"   קישור: {details_url}")

    print("\n" + "=" * 80)
    print(f"סיכום:")
    print(f"  סה\"כ בקשות: {len(permits)}")
    matching = [p for p in permits if p['matches_status']]
    print(f"  בקשות בסטטוס מתאים: {len(matching)}")
    print("=" * 80)

    return permits


if __name__ == "__main__":
    permits = analyze_page_html('page_2.html')

    # Save to JSON
    with open('page_2_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(permits, f, ensure_ascii=False, indent=2)

    print(f"\nתוצאות נשמרו ל: page_2_analysis.json")
