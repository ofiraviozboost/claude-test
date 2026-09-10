---
name: budget-control-agent
description: Run or continue a budget-control audit ("בקרה תקציבית") of Boost Moshavim's Monday.com data — finding supplier/consultant expenses billed without a matching client charge, collection stages that were never opened, old unresolved customer debts, and zero-amount collection bugs. Use this whenever the user asks for "בקרה תקציבית", "סוכן בקרה תקציבית", "תבדוק פערי תוספות", "תמשיך את הבקרה התקציבית", to audit budget/expense-vs-income gaps on Monday boards, or to pick up prior budget-control audit work — even if they don't name the skill explicitly.
---

# Budget Control Agent (סוכן בקרה תקציבית)

Audits Boost Moshavim's Monday.com boards for money that leaked out of the
budget-control process: a supplier got paid but the client was never billed
the matching amount, a collection stage that should have fired never did, or
a customer debt sat open for months unnoticed. This is real, ongoing work —
treat every run as a continuation of the same audit, not a one-off report.

The durable home for this audit is the SharePoint folder
`משרד\כספים\בקרה תקציבית\סוכן בקרה תקציבית` (OneDrive path, personal drive of
ofir@boost-k.com). It already holds a methodology doc and a findings
spreadsheet from prior runs — read them first via the Microsoft 365
connector (`sharepoint_search` / `read_resource`) before starting a new pass,
and update them (new file or revised rows) when you finish, rather than
treating each session's findings as disposable. Do not overwrite existing
files there without checking their contents first — someone may have added
manual findings alongside the agent's own.

## Data sources (Monday.com — workspace "Rewire", boost-moshavim.monday.com)

| Board | ID | Role |
|---|---|---|
| פרויקטים כספים | 5097957084 | Client income per project. Subitems board `5097957141`; each subitem's `color_mm41p5e` is `"חוזה בסיס"` or `"חוזה תוספת"`, amount in `numeric_mm41y19w`. |
| חוזים מול ספקים - פרויקטים | 1833596135 | Supplier/consultant expense per project. `color_mkswmtej` = `"בסיס"`/`"תוספות"`; `board_relation_mknbf3qk` links to the project (board `1833582108`); amount `numeric_mkv8vx71` (incl. VAT). |
| גביה מלקוחות | 1833585475 | Actual customer collections; has a saved "דוח חייבים" (debtors report) view. |
| תקבולים - בהקמה | 5101045460 | Actual receipts, linked back to a collection row. |
| פקודות לתשלום לספקים | 1833597366 | Supplier payment-order status (`color_mknb8pn5`: שולם / ממתין לאישור / etc.) and whether an invoice was received (`color_mknbvjys`). |
| ספקים | 1833590066 | Supplier cards. |
| פרויקטים | 1833582108 | The central (small, legacy-ish) project record; several other boards' `board_relation` columns point here. |

## The five checks

1. **Addendum expense with no addendum income** (the main one). Sum
   `"תוספות"`-tagged supplier costs per project (board 1833596135), then check
   whether that project has any `"חוזה תוספת"` subitem on the income side
   (5097957084 → 5097957141). A project with addendum expense but zero
   addendum income subitems is a candidate gap — but see "Before you flag a
   gap" below before reporting it as real.
2. **Collection stage never opened**. On the income subitems board
   (5097957141), the "יצירת גבייה 1–6" columns (`color_mm41gw25` etc.) should
   read `"כן"` once a stage's amount is set; a stage with a defined
   percentage/amount but the flag `"לא"` means the milestone was reached and
   billing was simply never created.
3. **Old unresolved debt**. Pull the "דוח חייבים" view on 1833585475, sort by
   creation date ascending. The company's own procedure escalates anything
   unpaid past 3 weeks to a manager meeting — anything far older than that is
   worth calling out by name and age.
4. **Zero-amount collections**. A known data-entry bug: an active collection
   row with amount 0 after VAT. Flag for cleanup/deletion.
5. **Negative balance in גביה מלקוחות** (found 26/08/2026, real production
   incident). Board 1833585475's `formula_mm5ze81z` ("יתרה") is normally 0 or
   positive (amount still owed). A **negative** value is the signature of a
   digit-entry typo in the receipt/receivable amount — e.g. a secretary typing
   an extra digit turns a ₪7,400 collection into ₪74,000, so
   `formula_mm5zk7fv` ("סה"כ התקבל") massively overshoots the actual invoice
   (`numeric_mm63dtj2`, "אחרי מע"מ") and the client appears to have overpaid
   by tens of thousands of shekels. This doesn't just misstate one row — it
   makes the client show up with a duplicate/extra balance entry elsewhere in
   the debtors view. Query with `board_insights`, `groupBy: ["name"]`,
   filter `formula_mm5ze81z` `lower_than` a threshold. **Use a threshold
   around -500, not 0** — dozens of rows sit at -0.0001 to -20 from ordinary
   VAT/rounding noise (confirmed 03/09/2026 weekly run) and are not real;
   anything beyond roughly -₪500 is worth surfacing.
6. **Collection rows with missing required links** (added 10/09/2026). A row
   on 1833585475 should always have a linked project
   (`board_relation_mknbkdj3`, "פרויקט מקושר") and a linked client
   (`board_relation_mknba1sh`, "לקוח מקושר"). `board_insights` with
   `groupBy: ["name"]` and a filter `operator: "is_empty"` on either column
   finds rows missing one — these can't be tied back to a project/client for
   reconciliation and should be filled in.
7. **Zero-amount collections created in the last week**. Same zero-amount bug
   as check #4, but scoped to freshly-created rows so it surfaces promptly:
   filter `__creation_log__` `within_the_last` `["DAYS", 7]` AND
   `numeric_mm63dtj2` ("אחרי מע"מ") `any_of` `[0]`.
8. **"Paid" status with an open balance** (found 10/09/2026, real production
   incident). A row whose `color_mknbj3g2` ("סטטוס") is `"תשלום מלא"` or
   `"תשלום מלא - אוטומטי"` should have `formula_mm5ze81z` ("יתרה") at ~0 — the
   status says fully paid, the balance should be settled. Filter
   `formula_mm5ze81z` `greater_than` `0.5` (again, ignore sub-shekel rounding
   noise) AND `color_mknbj3g2` `any_of` the "paid" label indexes; a hit means
   the row was marked paid without the payment actually being reconciled
   against it. Real example: "היתרים - ירון דה קלו - בסיס - אבן דרך 3" marked
   `"תשלום מלא - אוטומטי"` with a ₪25,488 balance still open.

## Before you flag a gap — check these first

An addendum-expense gap is only worth reporting once you've ruled out the
patterns below. Skipping this step is how you end up reporting a six-figure
"gap" that's actually a data-entry artifact — it happened in the first pass
of this audit and the numbers dropped by more than half after checking.

- **Base pricing often already covers the firm's own architecture/engineering.**
  A supplier cost tagged `"בסיס"` almost never needs a separate client
  charge — that's what the base contract price is for.
- **Addendum costs (surveys, external consultants — נגישות/אש/סניטרי/קרקע/**
  **תנועה/ניקוז/מיגון) are the ones that normally get billed to the client**
  **separately**, roughly in parallel with engaging the supplier, at about a
  20% margin. A `"תוספות"` supplier line with zero matching client billing is
  the real signal to chase.
- **Large bundled deals can fold named consultants into one lump base price.**
  A moshav-wide תב"ע master-plan contract, for instance, can have an explicit
  clause ("the price includes surveyor X, traffic consultant Y, drainage
  consultant Z") that legitimately makes several `"תוספות"`-tagged expense
  lines a mis-classification rather than a missed bill. Before reporting any
  gap above roughly ₪10,000, go read the actual signed quote/contract in the
  client's SharePoint folder (see below) rather than trusting the Monday tag.
- **Internal investment properties have no offsetting income by design** —
  company- or owner-held land bought for its own sake shows expense with no
  client and no recurring revenue; income only appears at eventual sale.
  Recognize these from context (no client attached, "השקעה"/"מגרש" in the
  name) and drop them, don't flag them.
- **The same client is often split into two parallel Monday projects** — one
  for "מגורים" (residential) scope, one for "חקלאי"/"פל\"ח" (agricultural)
  scope. Income (and sometimes the addendum billing) frequently lives under
  only one of the two, while supplier expense lines get split across both.
  Before concluding a "zero income" project is a real gap, search for a
  same-client sibling project (same name, different suffix — token-match on
  the client's name across board 5097957084's item names and board
  1833596135's resolved `board_relation_mknbf3qk` labels), pull its subitems,
  and unify both sides — income + expense, base + addendum — across the pair.
  Often the combined income already covers the combined expense.
  **But unifying the totals is not the same as confirming each sibling is
  correctly billed** — check the *per-sibling* breakdown too, not just the
  sum. A real case (אודי קרמר, 26/08/2026): unified addendum income (₪18,460)
  exceeded unified addendum expense (₪14,514), looking fully resolved — but
  broken down per sibling, one project ("היתר בית שלישי") held all ₪18,460 of
  income while the other two siblings had ₪0 income against real supplier
  costs (₪6,372 + ₪5,310). The aggregate zeroing-out was masking two real
  gaps. Always show the per-sibling table before calling a unified group
  "resolved".
- **Watch for duplicate/orphaned project records for the same client.** A
  quick giveaway: two items on board 5097957084 for what's obviously the same
  contract, one with only a single "ראשוני" subitem and no board_relation
  link to the legacy project board (`board_relation_mm41nt85` empty), the
  other fully fleshed out (linked, multiple subitems, matching base amount).
  The empty one is almost always an abandoned early stub — verify its sole
  subitem's amount matches the real one exactly (it usually does, no unique
  data to lose), then archive it with a raw GraphQL mutation via
  `all_api_write`: `mutation { archive_item(item_id: $id) { id } }`. Archiving
  is reversible (Monday's archive, not delete) — always archive, never
  hard-delete, and never do this without the user confirming first which one
  to keep.
- **A prior acknowledged write-off stays written off.** If the client already
  said "yes, that one's a mistake, we're eating the cost" for a specific
  project (check the methodology doc for these), don't re-flag it — note it
  as accepted-loss and move on.

## Cross-checking against Masterplan (the actual billing/collections system)

Monday's "חוזה תוספת" subitems record what *should* have been billed; the
real source of truth for what was actually invoiced and collected is
Masterplan, a separate system the user exports manually as `.xls` (old
coarse `תת חוזה` category field) or a richer `.xls` with a free-text `תיאור
חשבון` per line, grouped by `לקוח:` header blocks. When the user hands over
such a file:

- Parse it with `pandas.read_excel` (install `xlrd`/`openpyxl` if missing —
  neither is preinstalled). The richer client-grouped format needs a manual
  parser: forward-fill the client name from `לקוח:` header rows, keep only
  rows where the project-number column parses as numeric.
- Classify each line as base vs. addendum by keyword match on the
  description: `מדיד`, `יועצ`, `עורך בקשה`, `פענוח`, `אגרות`, `תוספת` →
  addendum; everything else → base. A line combining both (e.g. `תב"ע שלב ב'
  + עדכון מדידה`) can't be split automatically — flag it as "mixed" and
  either ask the user for the split (they often know it, e.g. "1,500 מזה
  שייך למדידה") or leave it out of the addendum sum with a note.
- Compare the addendum total actually collected (Masterplan, status `סגור`)
  against Monday's addendum expense for that project (unified across
  siblings). The difference is very often *not* a real gap — the billing
  happened, it just was never entered as a `חוזה תוספת` subitem in Monday.

**Fixing a confirmed gap**: if Masterplan shows real collected addendum
billing missing from Monday, create the missing subitem(s) on 5097957141
(`create_items`, `parentItemId` = the project's item on 5097957084,
`color_mm41p5e` = `{"label":"חוזה תוספת"}`, `numeric_mm41y19w` = amount) and
set its milestone-1 fields to reflect it's already collected:
`numeric_mm41j7np` (אחוז אבן דרך 1) = "100", `numeric_mm41v6kf` (סכום אבן
דרך 1) = the amount, `color_mm41gw25` (יצירת גבייה 1) =
`{"label":"שולם במאסטר"}`. **Never set that status to `"כן"`** (or leave it
for a real "yes, create a real collection now" case) — `"כן"` triggers a live
automation. `"שולם במאסטר"` is the safe label for "already collected outside
Monday, no automation needed."

**Stop at the contract/subitem level — do not touch גביה מלקוחות (1833585475)
or תקבולים (5101045460) as part of a fix**, even to mark them
"שולם במאסטר" there. Creating a גביה record on that board fires an automatic
reminder to the client regardless of the status you set (confirmed directly
by the user, 26/08/2026) — there's a "יצרת תקבול" button and a
"שליחת תזכורת" mechanism on that board that make it unsafe to touch during
an audit fix. Batch-entering גביה/תקבול for everything already marked
"שולם במאסטר" is a separate, deliberate task the user does on their own
schedule — never bundle it into a subitem-level fix.

## SharePoint contract verification

To check what a specific signed contract actually covers, search the
Microsoft 365 connector (`sharepoint_search`, `sharepoint_folder_search`,
`read_resource`) under paths like
`BOOST ניהול פרוקטים\לקוחות פרטיים1\<שם לקוח>` or
`...\מחלקה מקצועית\אגודות חקלאיות\<שם>` for files named like
"הצעת מחיר..." or "הסכם...". The pricing/scope clause is usually section 5
("התמורה") — read it for an explicit "the price includes X, Y, Z" statement
before deciding a gap is real vs. a classification error.

## Monday MCP tool gotchas (learned the hard way — save yourself the retries)

- `get_board_items_page` **fails** ("column type not supported") on any
  `board_relation` column whose settings list more than one target board
  (common for "project" and "customer" link columns here), and on
  `lookup`/`formula` columns that mirror through such a relation. Only
  `board_insights` reliably groups by these — use its `groupBy` on the
  board_relation column id; it returns a resolved `LABEL_<col>_0` name field.
- `board_insights` filters that try to restrict a `board_relation` column to
  a specific list of IDs are unreliable (often silently return null/empty).
  Don't filter board_relation by ID inside the tool call — pull the full
  `groupBy` result instead and filter it yourself afterward (jq/python).
- A subitems board (e.g. `5097957141`, "Subitems of פרויקטים כספים") has its
  **own item-id space** — separate both from its parent board's ids and from
  whatever board the parent's `board_relation` points to. To check "does
  project X have an addendum income subitem," join on the subitem's
  `parent_item_id` (a 5097957084 id), not by comparing it to a 1833582108
  project id directly. Crossing between the two id spaces is unreliable via
  the API — matching on the **exact project name** works well in practice,
  since names are kept in sync across the boards for the same project.
- A `get_board_items_page` / `board_insights` result that's too large gets
  saved to a local file instead of being printed — read it with `jq` or a
  short python script via Bash, not by paging through it line-by-line with
  Read (each row is one giant line).

## Department collections report (separate deliverable, added 10/09/2026)

A distinct recurring report the user asked for alongside the gap audit —
"how much did each department collect" (creation-based, not payment-based:
counts every collection row *created* in the period regardless of whether
it's actually been paid yet). Board 1833585475 already computes this:
`formula_mkxc2qw4` ("שם המחלקה") derives department from the row's
`multiple_person_mkw76eqf` owner via a `SWITCH` (מכירות / פרויקטים / מקצועית
/ "-" for unmapped people) — `board_insights` `groupBy` on it, `SUM` on
`numeric_mm633pmh` ("לפני מע"מ"), filtered by `__creation_log__`
`within_the_last` (`["DAYS", 7]` weekly, or the equivalent date range for
"previous calendar month" on a monthly run). This is a **separate email from
the gap-audit report** — don't merge them, the user explicitly asked for two
distinct emails on two cadences (every Thursday, and again on the 1st of the
month for the prior month).

## Output

When you've got clean results, produce:

1. A per-project table: project name, base-client(income), base-expense
   (supplier), addendum-client(income), addendum-expense(supplier),
   addendum-gap — after removing everything ruled out above. Total the gap
   column.
2. A short plain-language summary: what was checked, what it's for, what the
   number means (see the intro-card pattern in `references/pdf-report.md` for
   how the last PDF report worded this).

If asked for a PDF, follow `references/pdf-report.md` — it has the exact
Hebrew-RTL HTML/CSS template and the Chromium command that worked in this
sandbox (there's no other reliable HTML→PDF path here: no weasyprint, no
playwright python/node package — only the raw Chromium binary and a
LibreOffice `soffice` that renders styled HTML tables poorly).

## Onboarding a new report recipient (rule added 10/09/2026)

The first time any of these reports goes to someone who hasn't received one
before — a new name added to a distribution list, not just a routine weekly
run to existing recipients — send them a **full-context email first**, not
just that week's delta. A bare "here's what changed" email is meaningless to
someone with no baseline (real incident: office@boost-k.com got a "gap
dropped from ₪216,847 to ₪206,758" delta and had no idea what the ₪200K even
was or what was expected of her). The onboarding email should cover: what
this audit checks and why (base price vs. addendum billing, money leaking
when a supplier gets paid but the client isn't billed to match), the current
total and its breakdown by project, which parts are confirmed real vs. still
being verified, what's already been fixed, and what's actually expected of
*this* recipient (usually: receive the weekly update for visibility, flag
back if they know a business reason for a specific gap, and for
office/finance-facing recipients specifically, help chase the concrete
collections anomalies — negative balances, paid-but-open-balance rows).
Only send the routine's normal weekly delta after that.

## Contacts (context only — never message these people without being asked)

- עידן טיטו — idan@boost-k.com
- ניב יעקובי — niv@boost-k.com
- מנהלת משרד — office@boost-k.com
