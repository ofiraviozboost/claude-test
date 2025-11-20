#!/usr/bin/env python3
"""
סקריפט לחיפוש אוטומטי של בקשות בניה במערכת הועדה המקומית חוף השרון
מחפש בקשות במושב רשפון לפי קריטריונים ספציפיים
"""

import asyncio
import json
import re
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
import csv
from datetime import datetime


class CouncilSearchBot:
    """בוט לחיפוש בקשות בניה בועדה המקומית חוף השרון"""

    # סטטוסים לחיפוש
    TARGET_STATUSES = [
        "החלטה לאשר",
        "הפקת אגרה",
        "הושלם",
        "היתר",
        "היתר/טופס 4"
    ]

    # מילות מפתח לחיפוש
    KEYWORDS = ["פל״ח", "פלח", "בריכה"]

    # סף שטח (עיקרי + שירות)
    AREA_THRESHOLD = 320

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.results: List[Dict] = []

    async def start(self):
        """אתחול הדפדפן"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            # הגדרות נוספות לעבודה עם אתרים ישראליים
            locale='he-IL',
            timezone_id='Asia/Jerusalem'
        )

    async def close(self):
        """סגירת הדפדפן"""
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()

    async def search_permits(self, start_page: int = 1, max_pages: Optional[int] = None):
        """
        חיפוש בקשות בניה במושב רשפון

        Args:
            start_page: עמוד התחלה
            max_pages: מספר מקסימלי של עמודים (None = כל העמודים)
        """
        page = await self.context.new_page()

        current_page = start_page
        pages_processed = 0

        while True:
            if max_pages and pages_processed >= max_pages:
                break

            # בניית URL לעמוד הנוכחי
            url = self._build_search_url(current_page)

            print(f"\n🔍 עובר על עמוד {current_page}...")

            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)  # המתנה לטעינה מלאה

                # בדיקה אם יש תוצאות
                results_count = await self._count_results(page)
                if results_count == 0:
                    print("✓ הגעתי לסוף התוצאות")
                    break

                print(f"  נמצאו {results_count} תוצאות בעמוד")

                # עיבוד כל הבקשות בעמוד
                await self._process_page(page)

                current_page += 1
                pages_processed += 1

            except Exception as e:
                print(f"❌ שגיאה בעיבוד עמוד {current_page}: {e}")
                break

        await page.close()

    def _build_search_url(self, page_num: int) -> str:
        """בניית URL לחיפוש עם מספר עמוד"""
        base_url = "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/"
        params = {
            'searchType': 'ByTitle',
            'AddressPlace': '247',  # מושב רשפון
            'GushID': '',
            'HelkaID': '',
            'MigrashID': '',
            'page': str(page_num)
        }

        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"

    async def _count_results(self, page: Page) -> int:
        """ספירת מספר התוצאות בעמוד"""
        try:
            # נסה למצוא את השורות בטבלה
            rows = await page.locator('table tbody tr').count()
            return rows
        except:
            return 0

    async def _process_page(self, page: Page):
        """עיבוד כל הבקשות בעמוד אחד"""

        # קבלת כל השורות בטבלה
        rows = page.locator('table tbody tr')
        count = await rows.count()

        for i in range(count):
            try:
                row = rows.nth(i)

                # חילוץ נתונים מהשורה
                permit_data = await self._extract_row_data(row, page)

                if not permit_data:
                    continue

                # בדיקה אם הסטטוס תואם
                if not self._check_status(permit_data.get('status', '')):
                    continue

                print(f"  📄 בקשה: {permit_data.get('permit_number', 'N/A')} - {permit_data.get('status', 'N/A')}")

                # לחיצה על "פרטי הבקשה" ובדיקת תנאים
                details_link = row.locator('a:has-text("פרטי הבקשה"), a:has-text("פרטים")')

                if await details_link.count() > 0:
                    await self._check_permit_details(details_link.first, permit_data)

            except Exception as e:
                print(f"  ⚠️  שגיאה בעיבוד שורה {i}: {e}")
                continue

    async def _extract_row_data(self, row, page) -> Optional[Dict]:
        """חילוץ נתונים מהשורה"""
        try:
            cells = row.locator('td')
            cell_count = await cells.count()

            if cell_count == 0:
                return None

            data = {}

            # נסה לחלץ את מספר הבקשה
            first_cell = await cells.nth(0).inner_text()
            data['permit_number'] = first_cell.strip()

            # חילוץ סטטוס (בדרך כלל בעמודה אחת מהעמודות)
            for i in range(cell_count):
                cell_text = await cells.nth(i).inner_text()
                cell_text = cell_text.strip()

                # בדיקה אם זה סטטוס
                if any(status in cell_text for status in self.TARGET_STATUSES):
                    data['status'] = cell_text

            # חילוץ כתובת
            if cell_count > 2:
                address = await cells.nth(2).inner_text()
                data['address'] = address.strip()

            return data

        except Exception as e:
            print(f"  ⚠️  שגיאה בחילוץ נתונים: {e}")
            return None

    def _check_status(self, status: str) -> bool:
        """בדיקה אם הסטטוס תואם את הקריטריונים"""
        return any(target in status for target in self.TARGET_STATUSES)

    async def _check_permit_details(self, details_link, permit_data: Dict):
        """
        פתיחת דף פרטי הבקשה ובדיקת תנאים
        """
        # פתיחת כרטיסיה חדשה
        new_page = await self.context.new_page()

        try:
            # לחיצה על הקישור ופתיחה בכרטיסיה חדשה
            async with self.context.expect_page() as new_page_info:
                await details_link.click()

            new_page = await new_page_info.value
            await new_page.wait_for_load_state('networkidle', timeout=15000)

            # קבלת תוכן הדף
            content = await new_page.content()
            text_content = await new_page.inner_text('body')

            # בדיקת תנאים
            match_found = False
            match_reason = []

            # חיפוש מילות מפתח
            for keyword in self.KEYWORDS:
                if keyword in text_content:
                    match_found = True
                    match_reason.append(f"נמצא: {keyword}")

            # חיפוש שטחים
            area_match = self._check_area(text_content)
            if area_match:
                match_found = True
                match_reason.append(f"שטח: {area_match}")

            if match_found:
                print(f"    ✓ התאמה! {', '.join(match_reason)}")

                # חילוץ בעל עניין
                owner = await self._extract_owner(new_page)
                permit_data['owner'] = owner
                permit_data['match_reason'] = ', '.join(match_reason)
                permit_data['details_url'] = new_page.url

                self.results.append(permit_data)

                print(f"    👤 בעל עניין: {owner}")

            await new_page.close()

        except Exception as e:
            print(f"    ⚠️  שגיאה בבדיקת פרטים: {e}")
            if new_page and not new_page.is_closed():
                await new_page.close()

    def _check_area(self, text: str) -> Optional[str]:
        """
        בדיקה אם שטח עיקרי + שטח שירות > 320
        """
        # חיפוש דפוסים של שטח עיקרי ושטח שירות
        main_area_pattern = r'שטח עיקרי[:\s]+(\d+(?:\.\d+)?)'
        service_area_pattern = r'שטח (?:שירות|שרות)[:\s]+(\d+(?:\.\d+)?)'

        main_match = re.search(main_area_pattern, text)
        service_match = re.search(service_area_pattern, text)

        if main_match and service_match:
            main_area = float(main_match.group(1))
            service_area = float(service_match.group(1))
            total = main_area + service_area

            if total > self.AREA_THRESHOLD:
                return f"עיקרי {main_area} + שירות {service_area} = {total} > {self.AREA_THRESHOLD}"

        return None

    async def _extract_owner(self, page: Page) -> str:
        """חילוץ שם בעל העניין"""
        try:
            # נסה למצוא לשונית "בעלי עניין"
            owners_tab = page.locator('a:has-text("בעלי עניין"), button:has-text("בעלי עניין")')

            if await owners_tab.count() > 0:
                await owners_tab.first.click()
                await asyncio.sleep(1)

            # חיפוש שם בעל העניין בדרכים שונות
            patterns = [
                'text=בעל עניין',
                'text=בעל הנכס',
                'text=מבקש'
            ]

            for pattern in patterns:
                elements = page.locator(pattern)
                if await elements.count() > 0:
                    # נסה למצוא את השם ליד התווית
                    parent = elements.first.locator('..')
                    text = await parent.inner_text()

                    # חילוץ שם מהטקסט
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not any(x in line for x in ['בעל עניין', 'בעל הנכס', 'מבקש']):
                            return line

            # אם לא נמצא, נסה לחלץ מהטקסט הכללי
            text_content = await page.inner_text('body')
            owner_match = re.search(r'בעל (?:עניין|הנכס)[:\s]+([א-ת\s]+)', text_content)
            if owner_match:
                return owner_match.group(1).strip()

            return "לא נמצא"

        except Exception as e:
            print(f"    ⚠️  שגיאה בחילוץ בעל עניין: {e}")
            return "שגיאה"

    def save_results(self, filename: str = 'results.csv'):
        """שמירת תוצאות לקובץ CSV"""
        if not self.results:
            print("\n⚠️  לא נמצאו תוצאות לשמירה")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"council_search_{timestamp}.csv"

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'permit_number', 'status', 'address', 'owner',
                'match_reason', 'details_url'
            ])
            writer.writeheader()
            writer.writerows(self.results)

        print(f"\n✓ נשמרו {len(self.results)} תוצאות ל-{filename}")

    def save_results_json(self, filename: str = 'results.json'):
        """שמירת תוצאות לקובץ JSON"""
        if not self.results:
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"council_search_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"✓ נשמרו גם ל-JSON: {filename}")


async def main():
    """פונקציה ראשית"""
    print("=" * 60)
    print("🏗️  בוט חיפוש בקשות בניה - ועדה מקומית חוף השרון")
    print("=" * 60)

    bot = CouncilSearchBot(headless=False)  # headless=True להרצה ברקע

    try:
        await bot.start()

        # חיפוש בקשות (מתחיל מעמוד 1, ללא הגבלת עמודים)
        await bot.search_permits(start_page=1, max_pages=None)

        # שמירת תוצאות
        bot.save_results()
        bot.save_results_json()

        print("\n" + "=" * 60)
        print(f"✓ הסתיים! נמצאו {len(bot.results)} בקשות מתאימות")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
