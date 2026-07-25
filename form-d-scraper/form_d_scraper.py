#!/usr/bin/env python3
"""
SEC Form D scraper for PIVT ICO discovery.

Form D is the notice private issuers file with the SEC when they raise capital
under a Regulation D exemption. Independent sponsors, search funds, family
offices, and small PE firms file Form D for their acquisition SPVs -- so a fresh
Form D is a live "raising for a deal right now" buying signal. This is the free,
high-signal data source flagged in the ICO Discovery & Outreach report.

What it does
------------
1. Discover every Form D / D/A filing in a date range using EDGAR's public
   daily index (no API key, no search term needed -- captures ALL filings).
2. Fetch each filing's primary_doc.xml (the structured Form D data).
3. Parse ~30 fields: issuer, address, phone, executives/related persons,
   offering amount, amount sold, investor count, industry, exemptions, etc.
4. Write results to CSV and JSON.

Data source: SEC EDGAR (https://www.sec.gov). 100% free, public data.

Usage
-----
    python form_d_scraper.py --start 2026-07-20 --end 2026-07-24 \\
        --user-agent "PIVT Research yourname@pivt.com" --out pulls/

    # Quick smoke test: just the most recent business day, cap at 25 filings
    python form_d_scraper.py --start 2026-07-24 --end 2026-07-24 --limit 25 \\
        --user-agent "PIVT Research yourname@pivt.com"

SEC fair-access rules: you MUST send a User-Agent identifying you with a real
contact email, and stay under 10 requests/second. This script does both.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator, Optional
from xml.etree import ElementTree as ET

import requests

EDGAR_BASE = "https://www.sec.gov"
DAILY_INDEX_URL = EDGAR_BASE + "/Archives/edgar/daily-index/{year}/QTR{qtr}/form.{date}.idx"
FORM_TYPES = {"D", "D/A"}

# SEC asks for <= 10 req/s. We aim well under that to be a good citizen.
MIN_INTERVAL = 0.15  # seconds between requests (~6.6/s)
MAX_RETRIES = 4


class RateLimitedSession:
    """requests.Session that self-throttles and retries transient errors."""

    def __init__(self, user_agent: str):
        self.session = requests.Session()
        self.session.headers.update(
            {
                # SEC requires a descriptive UA with contact info.
                "User-Agent": user_agent,
                "Accept-Encoding": "gzip, deflate",
                "Host": "www.sec.gov",
            }
        )
        self._last = 0.0

    def get(self, url: str) -> requests.Response:
        for attempt in range(1, MAX_RETRIES + 1):
            # throttle
            wait = MIN_INTERVAL - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            try:
                resp = self.session.get(url, timeout=30)
            except requests.RequestException as exc:
                if attempt == MAX_RETRIES:
                    raise
                time.sleep(2 ** attempt)
                continue
            if resp.status_code == 200:
                return resp
            if resp.status_code == 404:
                resp.raise_for_status()
            # 403/429/5xx -> back off and retry
            if attempt == MAX_RETRIES:
                resp.raise_for_status()
            time.sleep(2 ** attempt)
        raise RuntimeError(f"unreachable: {url}")


@dataclass
class FormDRecord:
    """Flattened Form D filing -- one row per filing."""

    cik: str = ""
    accession: str = ""
    form_type: str = ""
    date_filed: str = ""
    filing_url: str = ""
    # issuer
    issuer_name: str = ""
    entity_type: str = ""
    jurisdiction: str = ""
    year_of_inc: str = ""
    street1: str = ""
    street2: str = ""
    city: str = ""
    state_or_country: str = ""
    zip_code: str = ""
    issuer_phone: str = ""
    # offering
    industry_group: str = ""
    investment_fund_type: str = ""
    is_amendment: str = ""
    date_of_first_sale: str = ""
    federal_exemptions: str = ""
    security_types: str = ""
    is_business_combination: str = ""
    minimum_investment: str = ""
    total_offering_amount: str = ""
    total_amount_sold: str = ""
    total_remaining: str = ""
    has_nonaccredited_investors: str = ""
    total_investors: str = ""
    sales_commissions: str = ""
    finders_fees: str = ""
    # people
    related_persons: str = ""  # "Name (Relationships); Name (Relationships)"
    signer_name: str = ""
    signer_title: str = ""
    signature_date: str = ""


def _q(date: dt.date) -> int:
    return (date.month - 1) // 3 + 1


def _text(node: Optional[ET.Element], path: str) -> str:
    """Namespace-agnostic single-value lookup by tag name."""
    if node is None:
        return ""
    for el in node.iter():
        if _localname(el.tag) == path and el.text:
            return el.text.strip()
    return ""


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _find(node: Optional[ET.Element], name: str) -> Optional[ET.Element]:
    if node is None:
        return None
    for el in node.iter():
        if _localname(el.tag) == name:
            return el
    return None


def _findall_direct(node: Optional[ET.Element], name: str) -> list[ET.Element]:
    if node is None:
        return []
    return [el for el in node.iter() if _localname(el.tag) == name]


def iter_form_d_filings(
    session: RateLimitedSession, start: dt.date, end: dt.date
) -> Iterator[dict]:
    """Yield {cik, accession, form_type, date_filed, filing_url} for each Form D."""
    day = start
    one = dt.timedelta(days=1)
    while day <= end:
        if day.weekday() >= 5:  # skip weekends (no EDGAR index published)
            day += one
            continue
        url = DAILY_INDEX_URL.format(
            year=day.year, qtr=_q(day), date=day.strftime("%Y%m%d")
        )
        try:
            resp = session.get(url)
        except requests.HTTPError as exc:
            # holidays / no filings that day -> 404, just skip
            if exc.response is not None and exc.response.status_code == 404:
                day += one
                continue
            raise
        for row in _parse_idx(resp.text):
            yield row
        day += one


def _parse_idx(text: str) -> Iterator[dict]:
    """Parse a daily form.YYYYMMDD.idx file, yielding Form D rows.

    Columns are fixed-position: Form Type, Company Name, CIK, Date Filed, File Name.
    We split on 2+ spaces which is robust to the variable-width columns.
    """
    import re

    started = False
    for line in text.splitlines():
        if not started:
            if set(line.strip()) == {"-"}:  # the dashed separator row
                started = True
            continue
        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) < 5:
            continue
        form_type, company, cik, date_filed, filename = parts[:5]
        if form_type not in FORM_TYPES:
            continue
        # filename like edgar/data/1234567/0001234567-26-000123.txt
        accession = filename.rsplit("/", 1)[-1].replace(".txt", "")
        acc_nodash = accession.replace("-", "")
        cik_clean = cik.lstrip("0") or cik
        filing_url = (
            f"{EDGAR_BASE}/Archives/edgar/data/{cik_clean}/{acc_nodash}/primary_doc.xml"
        )
        yield {
            "cik": cik,
            "accession": accession,
            "form_type": form_type,
            "date_filed": date_filed,
            "filing_url": filing_url,
            "company_index_name": company,
        }


def parse_form_d(xml_bytes: bytes, meta: Optional[dict] = None) -> FormDRecord:
    """Parse a Form D primary_doc.xml into a flat FormDRecord."""
    meta = meta or {}
    root = ET.fromstring(xml_bytes)
    rec = FormDRecord(
        cik=meta.get("cik", ""),
        accession=meta.get("accession", ""),
        form_type=meta.get("form_type", ""),
        date_filed=meta.get("date_filed", ""),
        filing_url=meta.get("filing_url", ""),
    )

    issuer = _find(root, "primaryIssuer")
    rec.issuer_name = _text(issuer, "entityName")
    rec.entity_type = _text(issuer, "entityType")
    rec.jurisdiction = _text(issuer, "jurisdictionOfInc")
    year = _find(issuer, "yearOfInc")
    rec.year_of_inc = _text(year, "value")
    addr = _find(issuer, "issuerAddress")
    rec.street1 = _text(addr, "street1")
    rec.street2 = _text(addr, "street2")
    rec.city = _text(addr, "city")
    rec.state_or_country = _text(addr, "stateOrCountry")
    rec.zip_code = _text(addr, "zipCode")
    rec.issuer_phone = _text(issuer, "issuerPhoneNumber")

    offering = _find(root, "offeringData")
    ig = _find(offering, "industryGroup")
    rec.industry_group = _text(ig, "industryGroupType")
    rec.investment_fund_type = _text(ig, "investmentFundType")
    rec.is_amendment = _text(offering, "isAmendment")
    first_sale = _find(offering, "dateOfFirstSale")
    rec.date_of_first_sale = (
        _text(first_sale, "value") or ("Yet to occur" if first_sale is not None and _find(first_sale, "yetToOccur") is not None else "")
    )
    exemptions = [e.text.strip() for e in _findall_direct(_find(offering, "federalExemptionsExclusions"), "item") if e.text]
    rec.federal_exemptions = "; ".join(exemptions)

    sec_types = _find(offering, "typesOfSecuritiesOffered")
    offered = []
    if sec_types is not None:
        for el in sec_types:
            if (el.text or "").strip().lower() == "true":
                offered.append(_localname(el.tag).replace("is", "").replace("Type", ""))
    rec.security_types = "; ".join(offered)

    bct = _find(offering, "businessCombinationTransaction")
    rec.is_business_combination = _text(bct, "isBusinessCombinationTransaction")
    rec.minimum_investment = _text(offering, "minimumInvestmentAccepted")

    amounts = _find(offering, "offeringSalesAmounts")
    rec.total_offering_amount = _text(amounts, "totalOfferingAmount")
    rec.total_amount_sold = _text(amounts, "totalAmountSold")
    rec.total_remaining = _text(amounts, "totalRemaining")

    investors = _find(offering, "investors")
    rec.has_nonaccredited_investors = _text(investors, "hasNonAccreditedInvestors")
    rec.total_investors = _text(investors, "totalNumberAlreadyInvested")

    commissions = _find(offering, "salesCommissionsFindersFees")
    sc = _find(commissions, "salesCommissions")
    rec.sales_commissions = _text(sc, "dollarAmount")
    ff = _find(commissions, "findersFees")
    rec.finders_fees = _text(ff, "dollarAmount")

    # related persons (execs / directors / promoters)
    people = []
    for person in _findall_direct(_find(root, "relatedPersonsList"), "relatedPersonInfo"):
        name = _find(person, "relatedPersonName")
        parts = [
            _text(name, "firstName"),
            _text(name, "middleName"),
            _text(name, "lastName"),
        ]
        full = " ".join(p for p in parts if p)
        rels = [r.text.strip() for r in _findall_direct(_find(person, "relatedPersonRelationshipList"), "relationship") if r.text]
        people.append(f"{full} ({', '.join(rels)})" if rels else full)
    rec.related_persons = "; ".join(people)

    sig = _find(root, "signatureBlock")
    rec.signer_name = _text(sig, "nameOfSigner")
    rec.signer_title = _text(sig, "signatureTitle")
    rec.signature_date = _text(sig, "signatureDate")

    return rec


def scrape(
    start: dt.date,
    end: dt.date,
    user_agent: str,
    limit: Optional[int] = None,
) -> list[FormDRecord]:
    session = RateLimitedSession(user_agent)
    records: list[FormDRecord] = []
    seen = 0
    for meta in iter_form_d_filings(session, start, end):
        if limit is not None and seen >= limit:
            break
        seen += 1
        try:
            resp = session.get(meta["filing_url"])
            rec = parse_form_d(resp.content, meta)
        except (requests.HTTPError, ET.ParseError) as exc:
            print(f"  ! skipped {meta['accession']}: {exc}", file=sys.stderr)
            continue
        records.append(rec)
        print(
            f"  [{len(records)}] {rec.issuer_name or meta['company_index_name']}"
            f" -- offering ${rec.total_offering_amount or '?'}"
            f" -- {rec.related_persons[:60]}",
            file=sys.stderr,
        )
    return records


def write_outputs(records: list[FormDRecord], out_dir: Path, tag: str) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"form_d_{tag}.csv"
    json_path = out_dir / f"form_d_{tag}.json"
    fields = list(FormDRecord().__dataclass_fields__.keys())
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for rec in records:
            writer.writerow(asdict(rec))
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump([asdict(r) for r in records], fh, indent=2)
    return csv_path, json_path


def _parse_date(s: str) -> dt.date:
    return dt.datetime.strptime(s, "%Y-%m-%d").date()


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Scrape SEC Form D filings from EDGAR.")
    p.add_argument("--start", required=True, type=_parse_date, help="YYYY-MM-DD")
    p.add_argument("--end", required=True, type=_parse_date, help="YYYY-MM-DD")
    p.add_argument(
        "--user-agent",
        required=True,
        help='SEC-required UA, e.g. "PIVT Research you@pivt.com"',
    )
    p.add_argument("--limit", type=int, default=None, help="cap number of filings")
    p.add_argument("--out", type=Path, default=Path("pulls"), help="output directory")
    args = p.parse_args(argv)

    if args.end < args.start:
        p.error("--end is before --start")

    print(
        f"Pulling Form D filings {args.start} -> {args.end} from SEC EDGAR ...",
        file=sys.stderr,
    )
    records = scrape(args.start, args.end, args.user_agent, args.limit)
    tag = f"{args.start:%Y%m%d}_{args.end:%Y%m%d}"
    csv_path, json_path = write_outputs(records, args.out, tag)
    print(
        f"\nDone. {len(records)} filings -> {csv_path} and {json_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
