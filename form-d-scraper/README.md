# SEC Form D scraper — PIVT ICO discovery

A small, free tool that turns SEC **Form D** filings into an outreach-ready list
of independent sponsors, search funds, family offices, and small PE firms — the
moment they raise capital for a deal.

This is the follow-up build to the *ICO Discovery & Outreach* report, which
flagged Form D as the highest-leverage free data source: private issuers file a
Form D when they raise under Regulation D, so a **fresh Form D is a live "raising
for a deal right now" buying signal** that better-funded competitors using
generic databases will miss.

---

## Why build directly against EDGAR instead of buying the Apify actor

The report costed the Apify EDGAR Form D actor at ~$2 per 1,000 results. That's
cheap, but the actor is just a wrapper around SEC EDGAR's **free public data**.
This script hits EDGAR directly, which means:

- **$0 per pull** (no per-result billing, no Apify account or token needed).
- **No middle layer** — you control the field mapping, the cadence, and where
  the data lands.
- Same ~30 fields the Apify actor returns (offering amount, investor count,
  executive names, issuer contact, etc.).

If you'd still rather run it inside Apify (e.g. for scheduling/UI), the "Apify
option" section below explains how — but you don't need it.

---

## What you get (per filing)

One row per filing, ~34 columns. Highlights:

| Field | Why it matters for outreach |
|---|---|
| `issuer_name`, `entity_type`, `jurisdiction` | Who filed; SPV vs. fund vs. LP |
| `related_persons` | **Executive / director / promoter names** — your actual contacts |
| `signer_name`, `signer_title` | The person who signed (often the GP / managing partner) |
| `city`, `state_or_country`, `issuer_phone` | Location + issuer phone (see caveat) |
| `industry_group`, `investment_fund_type` | Filters to PE / pooled-fund / operating-company raises |
| `total_offering_amount`, `total_amount_sold`, `total_remaining` | Deal size + how much is left to raise |
| `total_investors`, `minimum_investment` | Round shape |
| `is_business_combination` | Flags acquisition-type raises (independent-sponsor signal) |
| `date_of_first_sale`, `date_filed` | Freshness / timing of the signal |
| `federal_exemptions`, `security_types` | 506(b) vs 506(c), equity vs pooled fund |

See [`sample_output/`](sample_output/) for a full example row (CSV and JSON),
generated from the synthetic test fixture.

**Caveat (from the report):** the phone number belongs to the *issuer/SPV*, not
the executive's direct line. Use Form D to identify the **name + firm + signal**,
then run that person through Apollo / Sales Navigator for a direct email.

---

## Quick start

```bash
pip install -r requirements.txt

# Small test run — one business day, capped at 25 filings
python form_d_scraper.py \
  --start 2026-07-24 --end 2026-07-24 --limit 25 \
  --user-agent "PIVT Research yourname@pivt.com"

# A full week
python form_d_scraper.py \
  --start 2026-07-20 --end 2026-07-24 \
  --user-agent "PIVT Research yourname@pivt.com" \
  --out pulls/
```

Output lands in `pulls/form_d_<start>_<end>.csv` and `.json`.

> **The `--user-agent` is required and must contain a real contact email.** SEC
> fair-access rules require a descriptive User-Agent and a cap of 10 requests/sec.
> This script self-throttles to ~6/sec and retries transient errors. Don't strip
> the User-Agent — filings requests without one get blocked.

### About "how much data" — realistic volume

Roughly **300–500 Form D filings are filed per business day** across all
industries. Most are not ICOs (lots of real-estate and operating-company
raises). The next step (below) is to filter down to the PE / pooled-fund /
acquisition-SPV subset — that's where the independent sponsors are.

---

## How it works

1. **Discover** — reads EDGAR's public *daily index*
   (`/Archives/edgar/daily-index/YYYY/QTRn/form.YYYYMMDD.idx`) for each business
   day in the range and pulls every row whose form type is `D` or `D/A`. No
   search term needed — this captures **all** Form Ds, not just keyword hits.
2. **Fetch** — for each filing, downloads the structured
   `primary_doc.xml`.
3. **Parse** — flattens the XML into the ~34 fields above
   (`parse_form_d()` is namespace-agnostic, so it survives EDGAR schema-version
   bumps).
4. **Write** — CSV (for Sheets / Apollo import) and JSON (for enrichment
   pipelines).

---

## Suggested next filters (turn the raw pull into an ICO list)

Once you have a CSV, keep rows where **any** of these hold — these isolate the
independent-sponsor / small-PE segment:

- `industry_group` == `Pooled Investment Fund` **and** `investment_fund_type`
  in {`Private Equity Fund`, `Other Investment Fund`}
- `is_business_combination` == `true` (acquisition SPVs)
- `total_offering_amount` between ~$1M and ~$100M (lower-middle-market range)

Then dedupe by `related_persons` / firm and push the names into Apollo to find
verified emails.

---

## Running the "test run" from a network that can reach SEC

I built and tested the full pipeline here, but **could not do the live pull from
this environment** — its egress policy blocks `www.sec.gov`, `data.sec.gov`, and
`efts.sec.gov` (only package registries are allowed). So the parser is proven
end-to-end against a realistic synthetic fixture (`tests/`), and the one command
above will do the real pull on any normal machine or on a session whose network
policy allows `sec.gov`.

To verify the parser yourself right now (no network needed):

```bash
python tests/test_parser.py     # runs assertions + regenerates sample_output/
```

---

## The Apify option (if you want scheduling/UI instead)

If you'd rather run this inside Apify: use the **"SEC EDGAR Form D"** actor from
the Apify Store. Point it at a date range, run it, and export CSV. The fields map
1:1 to what this script produces. Budget ~$2 / 1,000 results plus a small
platform fee. You'd choose this only for the built-in scheduler/UI — the data
and cost are otherwise the same as running this script on a cron.

---

## Files

```
form-d-scraper/
├── form_d_scraper.py          # the scraper (CLI)
├── requirements.txt
├── tests/
│   ├── fixture_form_d.xml      # SYNTHETIC sample filing (not real)
│   └── test_parser.py          # asserts parser correctness + writes samples
└── sample_output/
    ├── form_d_SAMPLE_synthetic.csv
    └── form_d_SAMPLE_synthetic.json
```
