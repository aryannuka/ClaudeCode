"""Parser tests + sample-output generator.

Run directly to (a) verify the parser and (b) regenerate the sample_output/
files from the synthetic fixture so reviewers can see the exact data shape
without needing SEC network access:

    python tests/test_parser.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from form_d_scraper import parse_form_d, write_outputs  # noqa: E402

FIXTURE = Path(__file__).with_name("fixture_form_d.xml")
SAMPLE_DIR = Path(__file__).resolve().parents[1] / "sample_output"

FIXTURE_META = {
    "cik": "0001999888",
    "accession": "0001999888-26-000042",
    "form_type": "D",
    "date_filed": "2026-07-24",
    "filing_url": "https://www.sec.gov/Archives/edgar/data/1999888/000199988826000042/primary_doc.xml",
}


def test_parser_extracts_core_fields():
    rec = parse_form_d(FIXTURE.read_bytes(), FIXTURE_META)
    assert rec.issuer_name == "Cedar Ridge Acquisition Partners LP"
    assert rec.entity_type == "Limited Partnership"
    assert rec.jurisdiction == "DELAWARE"
    assert rec.city == "Nashville"
    assert rec.state_or_country == "TN"
    assert rec.issuer_phone == "615-555-0142"
    assert rec.industry_group == "Pooled Investment Fund"
    assert rec.investment_fund_type == "Private Equity Fund"
    assert rec.total_offering_amount == "18000000"
    assert rec.total_amount_sold == "7500000"
    assert rec.total_investors == "9"
    assert rec.minimum_investment == "250000"
    assert rec.is_business_combination == "true"
    assert "06b" in rec.federal_exemptions
    assert "Marcus Delgado" in rec.related_persons
    assert "Executive Officer" in rec.related_persons
    assert "Priya Anand" in rec.related_persons
    assert rec.signer_title == "Managing Partner"
    print("PASS: all core fields extracted correctly")


def generate_sample_output():
    rec = parse_form_d(FIXTURE.read_bytes(), FIXTURE_META)
    csv_path, json_path = write_outputs([rec], SAMPLE_DIR, "SAMPLE_synthetic")
    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    test_parser_extracts_core_fields()
    generate_sample_output()
