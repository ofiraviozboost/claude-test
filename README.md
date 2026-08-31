# בוט חיפוש בקשות בניה - ועדה מקומית חוף השרון

סקריפט אוטומטי לחיפוש בקשות בניה במושב רשפון במערכת הועדה המקומית חוף השרון.

## מה הסקריפט עושה?

הסקריפט מבצע את התהליך הידני הבא באופן אוטומטי:

1. ✅ נכנס למערכת איתור בקשות בניה של הועדה המקומית חוף השרון
2. ✅ בוחר את מושב רשפון
3. ✅ עובר עמוד אחרי עמוד על כל התוצאות
4. ✅ מסנן רק בקשות עם הסטטוסים:
   - החלטה לאשר
   - הפקת אגרה
   - הושלם
   - היתר
   - היתר/טופס 4
5. ✅ לוחץ על "פרטי הבקשה" של כל בקשה
6. ✅ מחפש בדף הפרטים:
   - מילות מפתח: "פל״ח", "פלח", "בריכה"
   - או: שטח עיקרי + שטח שירות > 320 מ"ר
7. ✅ אם נמצאה התאמה - מחלץ את שם בעל העניין
8. ✅ שומר את כל התוצאות לקובץ CSV ו-JSON

## התקנה

### דרישות מקדימות
- Python 3.8 ומעלה
- מערכת הפעלה: Windows, macOS או Linux

### שלבי התקנה

1. התקן את החבילות הנדרשות:
```bash
pip install -r requirements.txt
```

2. התקן את הדפדפנים של Playwright:
```bash
playwright install chromium
```

## שימוש

### הרצה בסיסית

```bash
python council_search.py
```

הסקריפט יפתח חלון דפדפן ויתחיל לעבוד. תוכל לראות את התהליך בזמן אמת.

### הרצה ברקע (ללא חלון דפדפן)

ערוך את הקובץ `council_search.py` ושנה:
```python
bot = CouncilSearchBot(headless=True)  # במקום headless=False
```

### הגבלת מספר עמודים

אם רוצה לבדוק רק כמה עמודים ראשונים:
```python
await bot.search_permits(start_page=1, max_pages=3)  # רק 3 עמודים
```

## קבצי פלט

הסקריפט יוצר 2 קבצים:

1. **council_search_YYYYMMDD_HHMMSS.csv** - טבלה עם העמודות:
   - מספר בקשה
   - סטטוס
   - כתובת
   - בעל עניין
   - סיבת התאמה
   - קישור לפרטי הבקשה

2. **council_search_YYYYMMDD_HHMMSS.json** - אותם נתונים בפורמט JSON

## התאמה אישית

### שינוי קריטריוני חיפוש

בקובץ `council_search.py`, תוכל לשנות:

#### סטטוסים לחיפוש:
```python
TARGET_STATUSES = [
    "החלטה לאשר",
    "הפקת אגרה",
    "הושלם",
    "היתר",
    "היתר/טופס 4"
]
```

#### מילות מפתח:
```python
KEYWORDS = ["פל״ח", "פלח", "בריכה"]
```

#### סף שטח:
```python
AREA_THRESHOLD = 320  # מ"ר
```

### חיפוש ביישוב אחר

שנה את הפרמטר `AddressPlace` ב-method `_build_search_url`:
```python
'AddressPlace': '247',  # רשפון - שנה לקוד של יישוב אחר
```

## פתרון בעיות

### הסקריפט לא פותח דפדפן
וודא ש-Playwright מותקן כראוי:
```bash
playwright install chromium
```

### שגיאת timeout
האתר עשוי להיות איטי. הגדל את ה-timeout:
```python
await page.goto(url, wait_until='networkidle', timeout=60000)  # 60 שניות
```

### לא נמצאו תוצאות
בדוק:
1. שהאתר זמין ונגיש
2. שקוד היישוב נכון (247 = רשפון)
3. שהסטטוסים נכתבים כמו באתר

## הערות

- ⚠️ הסקריפט תלוי במבנה האתר. אם האתר ישתנה, ייתכן שיצטרך עדכון
- ⏱️ התהליך יכול לקחת זמן, תלוי במספר הבקשות
- 🔍 הסקריפט שומר רק בקשות שעונות על הקריטריונים

## רישיון

MIT License

---

# סוכן Claude מחובר ל-WhatsApp

תיקיית `whatsapp_agent/` מכילה שרת webhook (FastAPI) שמחבר בין **WhatsApp Cloud API הרשמי של Meta** לבין **Claude API**: הודעה שמגיעה בוואטסאפ נשלחת ל-Claude, והתשובה נשלחת בחזרה כהודעת וואטסאפ.

> ⚠️ זה נבנה מול ה-API **הרשמי** של Meta בלבד. אין כאן שום שימוש בספריות "אוטומציה" לא רשמיות שמחקות משתמש (סיכון לחסימת חשבון), ואין הרצת סקריפטים חיצוניים ממקורות לא מאומתים.

## שלב 1: הגדרת WhatsApp Cloud API ב-Meta

1. היכנס ל-[Meta for Developers](https://developers.facebook.com/) וצור אפליקציה חדשה מסוג "Business".
2. הוסף את המוצר **WhatsApp** לאפליקציה.
3. בעמוד "API Setup" תמצא **מספר טלפון בדיקה (test number)** בחינם, ואת ה-**Phone Number ID** שלו.
4. צור **Permanent Access Token**: לך ל-Business Settings → System Users → צור System User → הענק לו הרשאות `whatsapp_business_messaging` על האפליקציה → Generate Token (בלי תפוגה).
5. ב-App Settings → Basic, שמור את ה-**App Secret** (ישמש לאימות חתימת ה-webhook).

## שלב 2: הגדרת סביבת העבודה המקומית

```bash
cp .env.example .env
# ערוך את .env ומלא: WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_APP_SECRET, ANTHROPIC_API_KEY
# ל-WHATSAPP_VERIFY_TOKEN בחר בעצמך מחרוזת אקראית - היא רק סיסמה בינך לבין Meta

pip install -r requirements.txt
uvicorn whatsapp_agent.app:app --reload --port 8000
```

## שלב 3: חשיפת השרת לאינטרנט (לפיתוח)

Meta דורש webhook עם HTTPS ציבורי. לפיתוח מקומי אפשר [ngrok](https://ngrok.com/):

```bash
ngrok http 8000
```

תקבל כתובת כמו `https://xxxx.ngrok-free.app`.

## שלב 4: רישום ה-webhook ב-Meta

בעמוד "WhatsApp → Configuration" באפליקציה:
- Callback URL: `https://xxxx.ngrok-free.app/webhook`
- Verify Token: אותו ערך שקבעת ב-`WHATSAPP_VERIFY_TOKEN`
- לחץ Verify and Save, ואז הירשם (Subscribe) לשדה `messages`.

## שלב 5: בדיקה

שלח הודעת WhatsApp למספר הבדיקה (מהמכשיר שרשמת כ"Recipient" ב-API Setup). ההודעה תעבור ל-Claude והתשובה תחזור אוטומטית.

## הערות לפני מעבר לפרודקשן

- מספר הבדיקה של Meta מוגבל ל-5 נמענים רשומים מראש. למספר אמיתי צריך אימות עסק (Business Verification) והוספת מספר טלפון קבוע.
- הרצה בפרודקשן דורשת שרת עם HTTPS אמיתי (לא ngrok) - למשל פריסה ל-Render/Fly.io/VM עם reverse proxy.
- ה-`WHATSAPP_TOKEN` וה-`ANTHROPIC_API_KEY` הם סודות רגישים - לעולם אל תעלה אותם ל-git (הם כבר ב-`.gitignore` דרך `.env`).
- הזיכרון בין הודעות (`whatsapp_agent/claude_client.py`) נשמר כרגע בזיכרון התהליך בלבד ונמחק בכל restart - לשימוש רציני שווה להעביר לאחסון קבוע (Redis/DB).
