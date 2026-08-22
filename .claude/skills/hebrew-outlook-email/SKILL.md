---
name: hebrew-outlook-email
description: Compose a Hebrew (or other RTL-language) email through the Microsoft 365 Outlook connector (outlook_create_draft / outlook_update_draft / outlook_send_mail). Use this whenever drafting or sending a Hebrew-language email via that connector, or whenever a Hebrew email draft comes back looking flat, left-aligned, or in a plain font — it explains what's actually achievable and how to get the best result within the connector's hard sanitizer limits.
---

# Hebrew / RTL email via the Outlook M365 connector

## The hard constraint — read this before trying to fix "ugly" formatting

The Outlook connector (`outlook_create_draft`, `outlook_update_draft`,
`outlook_send_mail`) sanitizes every HTML body against a narrow allowlist
**before** it ever reaches Outlook:

> Allowed tags: `p, br, a[href|name|target], b/strong, i/em, ul/ol/li,
> h1-h6, table/thead/tbody/tr/th/td, code, pre, hr, div, strike`. No other
> tags or attributes — no `style=`, `class=`, `id=`, `dir=`, images,
> scripts, or inline event handlers.

That means **`dir="rtl"` and any inline `style` (font-family, text-align,
color, table borders, spacing) are stripped or rejected outright** — this
was verified directly against the tool (a body containing `style=` or
`dir=` comes back `VALIDATION_ERROR: html_sanitize_rejected`). There is no
way to force a custom font or explicit right-to-left block alignment
through this connector. Don't spend time retrying `dir=` or `style=`
variations — it's not a bug to route around, it's the connector's
intentional anti-phishing/anti-injection guardrail, and it can't be
bypassed. Set expectations with the user accordingly rather than promising
a fully-styled result and then walking it back.

## What actually happens to Hebrew text without `dir`/`style`

Modern Outlook (web and desktop) applies its own auto-direction detection
per paragraph based on the first strong-directionality character it finds.
A `<p>` or `<div>` that **starts with a Hebrew character** typically renders
right-aligned and right-to-left on its own, with no markup needed. Problems
usually come from:

- A paragraph that starts with a number, Latin word, or punctuation before
  any Hebrew — put the Hebrew word first, or lead with an actual Hebrew
  character rather than a bullet symbol or digit.
- Mixed Hebrew/number lines (₪ amounts, dates) — these usually render fine
  inline via Unicode bidi; don't fight it, just proofread the *rendered*
  draft rather than assuming the source order is what displays.

## Getting a *good-looking* result within the allowlist

Since font/color/spacing are off the table, get visual quality from
**structure** instead — this is the whole game:

- Use real `<h2>`/`<h3>` for section headers, not a bold first sentence.
  Outlook's default heading styles (bold, larger, some margin) already read
  as "designed" without a single style attribute.
- **Avoid `<table>` for Hebrew content — confirmed broken in real testing.**
  Without `dir`, a table's cells fall back to LTR base direction even
  though surrounding paragraphs correctly auto-detect RTL. That mismatch
  garbles punctuation-adjacent Hebrew: `סה"כ פער בתוספות` rendered back as
  `כ פער בתוספות"סה` — the gershayim (`"`) and word order scrambled. Use
  `<ul>`/`<li>` for labeled numbers instead (`<li><b>סה"כ: 217,000 ₪</b></li>`)
  — bullets correctly right-align in the same test where the table did not.
- Use `<ul>`/`<ol>` for anything enumerable instead of writing "1. ... 2.
  ..." inline in a paragraph — Outlook's default list indentation and
  bullet styling is decent on its own, and (per above) actually renders
  Hebrew correctly where tables don't.
- Keep paragraphs short (2–3 sentences). Structural whitespace is the only
  "breathing room" you can add without CSS.
- Bold (`<b>`/`<strong>`) the one number or phrase that matters most in a
  paragraph — that's the only emphasis tool available.

## No attachments

`outlook_send_draft` explicitly re-validates against "no attachments" before
sending, and none of the create/update/send tools in this connector expose
an attachment parameter. If the user needs a file to travel with the email,
either:

- Link to a SharePoint/OneDrive location (upload via
  `sharepoint_upload_file`, embed the returned `webUrl` as an `<a>`), or
- Tell the user plainly that attachments aren't possible through this tool
  and they'll need to attach the file manually in their own Outlook client
  before sending (open the draft's `webLink`, add the attachment there, hit
  send themselves).

Don't imply you attached something you didn't — confirm what actually
travelled (a link) vs. what the human needs to do by hand.

## Workflow

1. Draft with `outlook_create_draft`, structured per the rules above.
2. If sending to third parties (not just the user), **show the rendered
   intent in chat first** and get explicit confirmation before calling
   `outlook_send_draft` — sending mail to other people is a one-way,
   externally-visible action.
3. If the user pastes back a screenshot of the draft looking wrong, that's
   the client's real rendering — trust the screenshot over your mental
   model of the HTML, and fix structurally (headers/tables/paragraph
   order), not by re-attempting `style=`/`dir=`.
