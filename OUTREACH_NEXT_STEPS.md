# PIVT outreach — next steps (follow-up to the ICO Discovery & Outreach report)

Companion to Joanna's three asks. Item 1 (Form D scraper) is built and lives in
[`form-d-scraper/`](form-d-scraper/). Items 2 and 3 are below.

---

## 1. SEC Form D scraper ✅ built

See [`form-d-scraper/README.md`](form-d-scraper/README.md). It pulls Form D
filings straight from SEC EDGAR (free, no Apify account needed), parses ~34
fields including executive names and offering size, and writes CSV/JSON. One
command does a small test run. The parser is proven end-to-end on a synthetic
fixture; the live pull runs on any network that can reach `sec.gov`.

---

## 2. Axial — partnership / distribution contact routes

The report's call was to approach Axial as a **partnership / distribution
channel**, not a data subscription. That framing is right, and there's a strong
precedent to lead with: Axial already runs **exclusive partnerships with member
associations** — most notably the Small Business Investor Alliance (SBIA), for
which Axial is the exclusive online deal-sourcing platform. So "PIVT as a
workflow/distribution partner for your independent-sponsor members" is a
conversation Axial is structurally set up to have.

**Verified public contact channels** (I did not invent individual names/emails —
these are the real, checkable routes):

| Route | Detail |
|---|---|
| Website | https://www.axial.net/ — general contact / "Request a demo" form |
| Team page | https://www.axial.net/whoweare/ — leadership names for a targeted, warm outreach |
| HQ | 443 Park Avenue South, 8th Floor, New York, NY 10016 |
| Phone | 800-860-4519 |
| LinkedIn | https://www.linkedin.com/company/axial — best route to named BD/partnerships staff via Sales Navigator |

**Recommended approach:**
1. Use **LinkedIn Sales Navigator** (once set up) to find the person who owns
   *partnerships / membership / BD* at Axial — that's the right door, not the
   sales team that gates the data product.
2. Open with the SBIA-style framing: PIVT as a deal-execution/workflow layer for
   their independent-sponsor and lower-middle-market members, i.e. a channel
   partnership, not a data buy.
3. Fall back to the website "request a demo/contact" form or the HQ line only if
   you can't get a warm LinkedIn intro.

> I've flagged where I'm confident (the channels above are public and current)
> vs. where I'm not (I won't put a specific person's name/email in writing
> without verifying it live — the team page + Sales Navigator will get you the
> right individual quickly).

---

## 3. Apollo free tier — this-week setup checklist

Goal from the report: Apollo is the outreach anchor (database + email finder +
verifier + sequencer in one). Start free, upgrade to Basic ($49/mo) only when you
hit export limits.

**Setup (≈20 min):**
1. Sign up at https://www.apollo.io with the PIVT domain email (better
   deliverability + company enrichment than a personal address).
2. Verify the email and connect your sending mailbox (Google/Microsoft) — this
   powers sequencing later.
3. Install the Apollo Chrome extension — it surfaces contacts directly on
   LinkedIn / Sales Navigator, which is exactly the discovery flow in the report.
4. Free-tier limits to plan around: ~5 mobile + 10 export credits, ~250
   emails/day, 2 active sequences. Fine for a first ICO list; upgrade when
   exports run out.

**First ICO list — recommended flow:**
1. In Apollo, build a saved search: titles like *Managing Partner, Principal,
   Founder, Independent Sponsor, Managing Director*; company types *Private
   Equity / Investment Management / Family Office*; headcount 1–50; geography US
   + Canada.
2. Cross-reference with the **Form D pull** from item 1 — the Form D names are
   your highest-intent leads (they're raising *right now*). Search each Form D
   `related_persons` name in Apollo to get a verified email, then drop them into
   a sequence.
3. Keep Sales Navigator for discovery/qualification (per the report), Apollo for
   finding-verifying-sending.

**On Sales Navigator:** you mentioned asking your LinkedIn contact about a
discount — worth doing; Core lists at ~$99/mo monthly, ~$90/mo annual, with a
30-day free trial you can start whenever you're ready to build the first list.

---

### Sources (Axial)
- [Axial — M&A and Capital Raising Platform for the Middle Market](https://www.axial.net/)
- [Axial — Meet the Team](https://www.axial.net/whoweare/)
- [Axial on LinkedIn](https://www.linkedin.com/company/axial)
- [SBIA selects Axial as exclusive online deal-sourcing network (Business Wire)](https://www.businesswire.com/news/home/20140604005512/en/The-Small-Business-Investor-Alliance-SBIA-Selects-Axial-as-Exclusive-Online-Deal-Sourcing-Network)
