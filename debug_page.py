#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale='he-IL',
            timezone_id='Asia/Jerusalem',
            ignore_https_errors=True
        )
        page = await context.new_page()

        url = "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/?searchType=ByAddress&AddressPlace=247&AddressStreet=&AddressStreetNumber=&page=1"

        print(f"🔍 ניווט ל: {url}\n")
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)

        # בדיקת מבנה הדף
        print("📄 כותרת הדף:")
        title = await page.title()
        print(f"  {title}\n")

        # בדיקת טבלה
        print("🔍 בדיקת טבלאות בדף:")
        tables = await page.locator('table').count()
        print(f"  נמצאו {tables} טבלאות\n")

        if tables > 0:
            # בדיקת שורות בטבלה הראשונה
            rows = await page.locator('table tbody tr').count()
            print(f"  שורות בטבלה: {rows}\n")

            if rows > 0:
                print("📋 5 השורות הראשונות:")
                for i in range(min(5, rows)):
                    row_text = await page.locator('table tbody tr').nth(i).inner_text()
                    print(f"  שורה {i+1}: {row_text[:100]}...")

        # בדיקת תוכן כללי
        print("\n📝 חלק מתוכן הדף:")
        body_text = await page.inner_text('body')
        print(body_text[:500])

        # שמירת screenshot
        await page.screenshot(path='page_debug.png')
        print("\n📸 Screenshot נשמר ל-page_debug.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
