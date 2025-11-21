# 🚀 איך להריץ את החיפוש האוטומטי המלא

## מה הסקריפט עושה?

**`full_auto_search.py`** - סקריפט אוטומטי **100%** שעושה הכל בשבילך:

✅ עובר על 20 עמודים ראשונים (או כמה שתרצה)
✅ מוצא בקשות בסטטוס: הושלם, היתר, טופס 4, החלטה לאשר, הפקת אגרה
✅ נכנס **אוטומטית** לכל בקשה ובודק:
   - מילות מפתח: פל״ח, בריכה
   - שטח עיקרי + שרות > 320 מ"ר
✅ מוציא שמות בעלי עניין
✅ שומר הכל ל-JSON מסודר
✅ עובד עם דפדפן אמיתי - אם יש CAPTCHA, תפתור פעם אחת והוא ימשיך לבד!

---

## התקנה מהירה (5 דקות)

### שלב 1: הורד את הקוד

```bash
git clone https://github.com/ofiraviozboost/claude-test.git
cd claude-test
git checkout claude/automate-permit-search-011t6Kek2G4m5kwnnhAVZbgj
```

### שלב 2: התקן חבילות Python

```bash
pip3 install -r requirements.txt
```

### שלב 3: התקן Chrome Driver

**Windows:**
1. הורד מ: https://chromedriver.chromium.org/
2. שים את הקובץ בתיקיית הפרויקט או ב-PATH

**Mac:**
```bash
brew install chromedriver
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# או הורד ידנית
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
```

---

## 🎯 הרצה - פשוט מאוד!

פשוט הרץ:

```bash
python3 full_auto_search.py
```

**זהו!**

### מה יקרה:

1. **דפדפן ייפתח** (Chrome/Firefox)
2. אם יש CAPTCHA - **תפתור אותו פעם אחת**
3. הסקריפט **ימשיך לבד**:
   - יעבור על 20 עמודים
   - ימצא בקשות בסטטוס הנכון
   - ייכנס לכל בקשה ויבדוק קריטריונים
   - ידפיס התקדמות בזמן אמת
4. **בסוף** תקבל קובץ JSON עם כל התוצאות

---

## ⚙️ התאמה אישית

פתח את `full_auto_search.py` ושנה:

### מספר עמודים לחיפוש:
```python
# שורה 330
MAX_PAGES_PER_PLACE = 20  # שנה ל-10, 50, 100, וכו'
```

### עמוד התחלה:
```python
# שורה 331
START_PAGE = 1  # אם תרצה להתחיל מעמוד 5, שנה ל-5
```

### מקומות נוספים:
```python
# שורות 323-327
PLACES = {
    "רשפון": "247",
    "כפר שמריהו": "XXX",  # הוסף מספר מקום
    "הרצליה": "XXX",       # הוסף מספר מקום
}
```

**איך למצוא מספר מקום?**
1. פתח את האתר בדפדפן
2. בחר את המקום
3. תראה בכתובת: `AddressPlace=XXX`
4. זה המספר!

### קריטריונים:
```python
# שורות 27-29
self.target_statuses = ["הושלם", "היתר", "טופס 4", "החלטה לאשר", "הפקת אגרה"]
self.keywords = ["פל״ח", "בריכה", "פלח"]
self.area_threshold = 320  # שטח מינימלי במ"ר
```

---

## 📊 תוצאות

אחרי ההרצה תקבל קבצים:

```
results_רשפון_20250121_143052.json    ← תוצאות רשפון
results_כפר_שמריהו_20250121_143752.json  ← תוצאות כפר שמריהו
results_all_places_20250121_144000.json   ← כל התוצאות ביחד
```

### מבנה קובץ JSON:

```json
[
  {
    "permit_number": "1/20250004",
    "status": "החלטה לאשר",
    "address": "רחוב סמ הרקפת 6, רשפון",
    "applicant": "סלטי רומי",
    "description": "תוספת למבנה קיים",
    "details_url": "https://...",
    "keyword_found": true,
    "keywords_matched": ["בריכה"],
    "area_match": false,
    "main_area": 200,
    "service_area": 50,
    "total_area": 250,
    "owners": ["סלטי רומי", "שרה כהן"]
  }
]
```

---

## 🎬 דוגמת הרצה

```
================================================================================
🤖 FULL AUTOMATED PERMIT SEARCH
================================================================================

This script will:
  1. Search through pages of permits
  2. Find permits with target statuses
  3. Check each for keywords (פל״ח, בריכה) or large area (>320 sqm)
  4. Extract owner information
  5. Save everything to JSON

================================================================================

Will search:
  - רשפון: pages 1-20

Press Enter to start, or Ctrl+C to cancel...

[הקש Enter]

✅ Chrome driver initialized

================================================================================
🔍 Starting search for רשפון
   Pages: 1 to 20
   Target statuses: הושלם, היתר, טופס 4, החלטה לאשר, הפקת אגרה
================================================================================

📄 Page 1/20
--------------------------------------------------------------------------------
   Found 3 permits with matching status
   1. 1/20250004 - סלטי רומי
      Analyzing: 1/20250004
         ✅ Keywords: בריכה
         👤 Owners: סלטי רומי
      ✅✅ MATCH! Added to results
   2. 1/20240353 - מורן יובל
      Analyzing: 1/20240353
      ❌ No match (no keywords/area)
   ...

📄 Page 2/20
--------------------------------------------------------------------------------
   ...

================================================================================
📊 SEARCH COMPLETE - Found 15 matching permits
================================================================================

1. 1/20250004
   Status: החלטה לאשר
   Address: רחוב סמ הרקפת 6, רשפון
   Applicant: סלטי רומי
   ✅ Keywords: בריכה
   👤 Owners: סלטי רומי
   🔗 https://vaada.hof-hasharon.co.il/...

...

💾 Results saved to: results_רשפון_20250121_143052.json
✅ All results saved to: results_all_places_20250121_144000.json

Closing browser...
✅ Done!
```

---

## ⏱️ כמה זמן זה לוקח?

- **עמוד אחד:** ~30 שניות
- **20 עמודים:** ~10-15 דקות
- **תלוי ב:**
  - כמה בקשות יש בכל עמוד
  - כמה מהן בסטטוס הנכון
  - מהירות האתר

**טיפ:** תתחיל עם 5 עמודים בלבד (`MAX_PAGES_PER_PLACE = 5`) כדי לראות שזה עובד!

---

## ❓ פתרון בעיות

### "chromedriver not found"
לא התקנת Chrome driver. ראה שלב 3 למעלה.

### "No module named 'selenium'"
לא התקנת חבילות:
```bash
pip3 install -r requirements.txt
```

### הדפדפן נסגר מיד
הוסף breakpoint בסוף הסקריפט או הרץ עם debug mode.

### CAPTCHA לא נפתר אוטומטית
זה נורמלי - פתור אותו ידנית והסקריפט ימשיך.

### האתר איטי
הגדל את זמני ההמתנה בקוד:
```python
time.sleep(3)  # שנה ל-5 או יותר
```

---

## 💡 טיפים

1. **התחל קטן:** 5 עמודים, ראה שזה עובד, אז תגדיל
2. **הרץ בלילה:** אם יש הרבה עמודים, תן לו לרוץ בזמן שאתה ישן
3. **בדוק בדרך:** הסקריפט שומר תוצאות ביניים - אפשר לעצור ולראות מה נמצא
4. **מושבים מרובים:** הוסף עוד מושבים ל-PLACES והסקריפט יעבור על כולם

---

## 🎯 זהו! פשוט להפליא

רק 3 צעדים:
1. התקן Chrome driver (פעם אחת)
2. הרץ: `python3 full_auto_search.py`
3. תהנה מהתוצאות! 🎉

---

**צריך עזרה?** פתח issue בגיטהאב או שלח הודעה!
