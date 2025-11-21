# Automated Permit Search - Hof HaSharon Committee

סקריפט אוטומטי לחיפוש היתרי בנייה בוועדה המקומית חוף השרון.

## תיאור

הסקריפט מבצע את התהליך הבא באופן אוטומטי:
1. מחפש היתרי בנייה במושב רשפון
2. מסנן לפי סטטוס: "הושלם", "היתר", "טופס 4"
3. עובר על כל העמודים
4. בודק כל היתר אם הוא עונה על הקריטריונים:
   - מכיל מילות מפתח: "פל״ח", "בריכה"
   - **או** שטח עיקרי + שרות > 320 מ"ר
5. מוציא את שמות בעלי העניין של היתרים שעונים על הקריטריונים

## דרישות מערכת

- Python 3.7 ומעלה
- חיבור לאינטרנט

## התקנה

```bash
# התקן את החבילות הנדרשות
pip3 install -r requirements.txt
```

## שימוש

### הרצה מלאה (כל העמודים)

```bash
python3 permit_search.py
```

הסקריפט יעבור על כל העמודים ויציג:
- התקדמות בזמן אמת
- כל היתר שנמצא שעונה על הקריטריונים
- בסוף - סיכום ושמירה לקובץ JSON

### בדיקה מהירה (עמוד ראשון בלבד)

```bash
python3 test_permit_search.py
```

### תוצאות

התוצאות נשמרות בקובץ: `permit_search_results.json`

כל תוצאה כוללת:
- מספר היתר
- קישור לפרטי ההיתר
- האם נמצאה מילת מפתח
- האם השטח עובר את הסף
- רשימת בעלי עניין

## הערות חשובות

### CAPTCHA
אם האתר מציג CAPTCHA, הסקריפט לא יוכל לעבוד אוטומטית. פתרונות:

1. **שימוש ב-Selenium עם דפדפן אמיתי:**
   ```bash
   python3 permit_search_selenium.py
   ```
   הסקריפט הזה יפתח דפדפן שבו תוכל לפתור את ה-CAPTCHA ידנית.

2. **שימוש בסשן קיים:**
   - פתח את האתר בדפדפן רגיל
   - התחבר ופתור את ה-CAPTCHA
   - העתק cookies מהדפדפן לסקריפט

### מגבלות קצב (Rate Limiting)

הסקריפט כולל המתנה של 1-2 שניות בין כל בקשה כדי לא להעמיס על השרת.
אם תקבל שגיאות 429 (Too Many Requests), הגדל את זמני ההמתנה.

### התאמה אישית

ניתן לשנות את הקריטריונים בקוד:

```python
# בקובץ permit_search.py, בתוך __init__:

# שינוי סטטוסים מבוקשים
self.target_statuses = ["הושלם", "היתר", "טופס 4"]

# שינוי מילות מפתח
self.keywords = ["פל״ח", "בריכה", "פלח"]

# שינוי סף שטח
self.area_threshold = 320
```

## מבנה הקבצים

```
.
├── permit_search.py          # סקריפט ראשי - חיפוש מלא
├── test_permit_search.py     # סקריפט בדיקה - עמוד אחד בלבד
├── permit_search_selenium.py # גרסה עם Selenium (אופציונלי)
├── requirements.txt          # תלויות Python
├── README.md                 # קובץ זה
└── permit_search_results.json # תוצאות (נוצר אוטומטית)
```

## פתרון בעיות

### "Connection timeout"
- בדוק חיבור לאינטרנט
- נסה שוב - ייתכן שהשרת עמוס
- הגדל את ה-timeout בקוד:
  ```python
  response = self.session.get(url, timeout=60)  # 60 שניות במקום 30
  ```

### "Could not find results table"
- מבנה האתר השתנה
- צריך לעדכן את ה-selectors בקוד
- פנה למפתח לעדכון

### "No owner information found"
- לא כל היתר מכיל מידע על בעלים בציבורי
- נסה לגשת לאתר ידנית ולבדוק אם המידע מופיע

## פיתוח והרחבה

### הוספת קריטריונים נוספים

ערוך את המתודה `check_permit_details`:

```python
def check_permit_details(self, details_url: str) -> Optional[Dict]:
    # ... קוד קיים ...

    # הוסף קריטריון חדש
    my_custom_check = "מילה מיוחדת" in page_text

    if keyword_found or area_match or my_custom_check:
        # ...
```

### חיפוש במקומות נוספים

שנה את `base_search_url` ב-`main()`:

```python
# מצא את מספר המקום (Place ID) באתר הועדה
base_search_url = "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/?searchType=ByAddress&AddressPlace=XXX&page=1"
```

## רישיון

MIT License - ראה LICENSE

## תמיכה

לבעיות או שאלות, פתח issue בגיטהאב או צור קשר ישירות.

---

**שימו לב:** הסקריפט הזה מיועד לשימוש אישי בלבד. שימוש במידע מהאתר חייב להיות בהתאם לתנאי השימוש של אתר הועדה המקומית.
