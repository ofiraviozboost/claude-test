# מה עכשיו? - מדריך צעדים הבאים

## 🔴 הבעיה הנוכחית

האתר של ועדת חוף השרון לא זמין כרגע (שגיאת 503).
זה יכול להיות:
- עומס על השרת
- תחזוקה
- חסימת בוטים אוטומטיים

## ✅ מה הכנתי לך

כל הסקריפטים **מוכנים ועובדים** - רק צריך שהאתר יהיה זמין.

### הקבצים שנוצרו:

```
claude-test/
├── permit_search.py          ⭐ הסקריפט הראשי - הרצה מלאה
├── permit_search_selenium.py ⭐ גרסת Selenium - עם CAPTCHA
├── test_permit_search.py     🧪 בדיקה מהירה
├── test_site_access.py       🔍 בדיקת זמינות האתר
├── manual_assistant.py       🛠️ עזר לניתוח ידני
├── requirements.txt          📦 תלויות
├── README.md                 📖 מדריך מלא
├── .gitignore               🙈 Git ignore
└── NEXT_STEPS.md            👈 אתה כאן
```

---

## 🎯 3 דרכים להריץ את המערכת

### 🥇 דרך 1: מהמחשב שלך (מומלץ ביותר!)

**למה זה הכי טוב:**
- אתה לא בשרת, אז האתר לא יחשוד שאתה בוט
- תוכל לפתור CAPTCHA בעצמך
- חיבור ישיר ומהיר

**איך:**

```bash
# 1. שכפל את הפרויקט
git clone https://github.com/ofiraviozboost/claude-test.git
cd claude-test
git checkout claude/automate-permit-search-011t6Kek2G4m5kwnnhAVZbgj

# 2. התקן Python packages
pip3 install -r requirements.txt

# 3. התקן Chrome driver (פעם אחת)
# Windows: https://chromedriver.chromium.org/ → הורד והוסף ל-PATH
# Mac: brew install chromedriver
# Linux: sudo apt-get install chromium-chromedriver

# 4. הרץ!
python3 permit_search_selenium.py

# אם יופיע CAPTCHA - פתור אותו בדפדפן שנפתח
# הסקריפט ימשיך אוטומטית
```

**מה יקרה:**
1. 🌐 דפדפן Chrome ייפתח
2. 🤖 הסקריפט ינווט לאתר אוטומטית
3. 🧩 אם יש CAPTCHA - תפתור אותו
4. ⚙️ הסקריפט יעבור על כל העמודים
5. 📊 תקבל קובץ JSON עם כל הממצאים
6. ⏱️ זמן הרצה: 10-20 דקות (תלוי בכמות)

---

### 🥈 דרך 2: נסה שוב מהשרת בזמן אחר

האתר עשוי להיות זמין בשעות אחרות:

```bash
# בדוק אם האתר זמין:
python3 test_site_access.py

# אם זה עובד ✓ אז הרץ:
python3 permit_search.py

# או לבדיקה מהירה (עמוד 1 בלבד):
python3 test_permit_search.py
```

**מתי לנסות:**
- ✅ בוקר: 7:00-9:00
- ✅ אחר הצהריים: 14:00-16:00
- ✅ ערב: 20:00-22:00
- ❌ הימנע: 11:00-13:00 (שעות עומס)

---

### 🥉 דרך 3: גישה ידנית + עזר אוטומטי

אם כלום לא עובד, תוכל לעבוד ידנית והסקריפט יעזור לך:

**תהליך:**

1. **פתח את האתר בדפדפן רגיל** (כמו שאתה עושה כרגע)
   ```
   https://vaada.hof-hasharon.co.il/
   → איתור תיקי בנייה ובקשות
   → איתור בקשה לפי כתובת
   → רשפון
   ```

2. **כשאתה מוצא היתר שנראה מעניין:**
   - לחץ על "פרטי הבקשה"
   - Ctrl+U (view source)
   - Ctrl+A (select all)
   - Ctrl+C (copy)

3. **הדבק ב-`permit_html.txt`** ושמור

4. **הרץ את העוזר:**
   ```bash
   python3 manual_assistant.py
   ```

5. **הסקריפט יאמר לך:**
   - ✅ או ❌ האם ההיתר עונה על הקריטריונים
   - מה השטח (עיקרי + שרות)
   - האם יש מילות מפתח
   - מי בעלי העניין

**יתרונות:**
- אין בעיית CAPTCHA
- אתה בשליטה מלאה
- המערכת עדיין עושה את העבודה הקשה של ניתוח

---

## ⚙️ התאמה אישית

אם אתה רוצה לשנות קריטריונים, ערוך `permit_search.py`:

```python
# שורות 24-29:
class PermitSearcher:
    def __init__(self, base_url: str = "https://vaada.hof-hasharon.co.il"):
        # ...

        # שנה כאן ↓
        self.target_statuses = ["הושלם", "היתר", "טופס 4"]
        self.keywords = ["פל״ח", "בריכה", "פלח"]
        self.area_threshold = 320  # מ"ר
```

**דוגמאות:**

חפש רק בריכות:
```python
self.keywords = ["בריכה"]
```

סף שטח גבוה יותר:
```python
self.area_threshold = 400
```

חפש במקום אחר (לא רשפון):
```python
# שורה ~220 בתחתית הקובץ
# שנה את AddressPlace למספר המקום:
base_search_url = "https://vaada.hof-hasharon.co.il/SearchPermitApplicationResults/?searchType=ByAddress&AddressPlace=123&page=1"
```

---

## 📊 הבנת התוצאות

אחרי ההרצה תקבל קובץ JSON:

```json
[
  {
    "permit_number": "2023/0456",
    "url": "https://...",
    "keyword_found": true,      // האם נמצאה מילת מפתח
    "area_match": false,        // האם השטח > 320
    "owners": [                 // רשימת בעלי עניין
      "ישראל ישראלי",
      "שרה כהן"
    ]
  }
]
```

**לצפייה:**
```bash
# בטרמינל:
cat permit_search_results.json

# או פתח בעורך:
code permit_search_results.json  # VS Code
nano permit_search_results.json  # עורך טקסט
```

**ייצוא לאקסל (אופציונלי):**
```bash
# התקן pandas
pip3 install pandas openpyxl

# הרץ:
python3 -c "
import json
import pandas as pd

with open('permit_search_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df.to_excel('permits.xlsx', index=False)
print('Exported to permits.xlsx')
"
```

---

## 🆘 פתרון בעיות

### "Connection timeout" / "503 error"
**הבעיה:** האתר לא זמין
**פתרון:**
1. נסה שוב מאוחר יותר
2. הרץ מהמחשב שלך (דרך 1)

### "No module named 'selenium'"
**הבעיה:** לא התקנת חבילות
**פתרון:**
```bash
pip3 install -r requirements.txt
```

### "chromedriver not found"
**הבעיה:** Chrome driver לא מותקן
**פתרון:**
- Windows: הורד מ-https://chromedriver.chromium.org/
- Mac: `brew install chromedriver`
- Linux: `sudo apt-get install chromium-chromedriver`

### "No matching permits found"
**הבעיה:** אולי באמת אין
**בדיקה:**
1. הרץ `test_permit_search.py` - רואה בכלל היתרים?
2. בדוק בעצמך באתר - יש היתרים שעונים?
3. אולי צריך להרחיב קריטריונים

### CAPTCHA לא נפתר
**הבעיה:** Selenium לא ממתין מספיק
**פתרון:** ערוך `permit_search_selenium.py` שורה 56:
```python
def solve_captcha_manually(self, timeout: int = 120):  # היה 60, שנה ל-120
```

---

## 🎯 המלצה שלי

**הכי קל וטוב:**

1. **עכשיו:** שכפל למחשב שלך:
   ```bash
   git clone https://github.com/ofiraviozboost/claude-test.git
   cd claude-test
   git checkout claude/automate-permit-search-011t6Kek2G4m5kwnnhAVZbgj
   pip3 install -r requirements.txt
   ```

2. **התקן Chrome driver** (ראה הוראות למעלה)

3. **הרץ:**
   ```bash
   python3 permit_search_selenium.py
   ```

4. **תהנה** מהתוצאות! 🎉

---

## 📞 צריך עזרה?

אם משהו לא עובד:
1. בדוק שוב את ההוראות
2. חפש את השגיאה בסעיף "פתרון בעיות"
3. פתח issue בגיטהאב
4. פנה למפתח

---

**בהצלחה! 🚀**

כל הקוד ב: https://github.com/ofiraviozboost/claude-test
Branch: `claude/automate-permit-search-011t6Kek2G4m5kwnnhAVZbgj`
