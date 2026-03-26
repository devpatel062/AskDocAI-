from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any
from json import JSONDecodeError

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
DEFAULT_BROAD_QUERY = (
    "(disease[Title/Abstract] OR disorder[Title/Abstract] OR syndrome[Title/Abstract] "
    "OR infection[Title/Abstract] OR cancer[Title/Abstract] OR diabetes[Title/Abstract] "
    "OR hypertension[Title/Abstract] OR asthma[Title/Abstract] OR stroke[Title/Abstract] "
    "OR cardiovascular[Title/Abstract] OR kidney[Title/Abstract] OR liver[Title/Abstract] "
    "OR neurological[Title/Abstract] OR autoimmune[Title/Abstract] OR psychiatric[Title/Abstract])"
)


def _request(url: str, params: dict[str, Any]) -> bytes:
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    with urllib.request.urlopen(full_url, timeout=60) as response:
        return response.read()


def _get_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join("".join(element.itertext()).split())


def _parse_esearch_id_list(raw: bytes) -> list[str]:
    text = raw.decode("utf-8", errors="replace")

    # Preferred format from E-utilities is JSON, but some error responses arrive as XML.
    try:
        payload = json.loads(text)
        error_text = payload.get("esearchresult", {}).get("ERROR")
        if error_text:
            raise ValueError(f"PubMed ESearch error: {error_text}")
        ids = payload.get("esearchresult", {}).get("idlist", [])
        return [str(item) for item in ids if str(item).strip()]
    except JSONDecodeError:
        pass

    try:
        root = ET.fromstring(text)
        ids = []
        for node in root.findall(".//IdList/Id"):
            value = (node.text or "").strip()
            if value:
                ids.append(value)
        if ids:
            return ids

        err = root.find(".//ERROR")
        if err is not None and (err.text or "").strip():
            raise ValueError(f"PubMed ESearch error: {(err.text or '').strip()}")
    except ET.ParseError:
        pass

    preview = text[:300].replace("\n", " ")
    raise ValueError(f"Unable to parse PubMed ESearch response. First 300 chars: {preview}")


def _esearch_ids(
    term: str,
    email: str,
    batch_size: int,
    max_records: int,
    start_year: int | None,
    end_year: int | None,
) -> list[str]:
    ids: list[str] = []
    retstart = 0

    while len(ids) < max_records:
        # PubMed ESearch cannot paginate beyond the first 9,999 records for one query window.
        if retstart > 9998:
            break

        remaining = max_records - len(ids)
        retmax = min(batch_size, remaining)

        if retstart + retmax > 9999:
            retmax = max(1, 9999 - retstart)

        params: dict[str, Any] = {
            "db": "pubmed",
            "term": term,
            "retmode": "json",
            "retstart": retstart,
            "retmax": retmax,
            "sort": "relevance",
            "email": email,
            "tool": "askdocai_importer",
        }

        if start_year is not None:
            params["mindate"] = str(start_year)
            params["datetype"] = "pdat"
        if end_year is not None:
            params["maxdate"] = str(end_year)
            params["datetype"] = "pdat"

        raw = _request(ESEARCH_URL, params)
        batch_ids = _parse_esearch_id_list(raw)
        if not batch_ids:
            break

        ids.extend(batch_ids)
        retstart += len(batch_ids)
        time.sleep(0.34)

    return ids[:max_records]


def _esearch_ids_chunked_by_year(
    term: str,
    email: str,
    batch_size: int,
    max_records: int,
    start_year: int,
    end_year: int,
) -> list[str]:
    ids: list[str] = []

    for year in range(end_year, start_year - 1, -1):
        if len(ids) >= max_records:
            break

        remaining = max_records - len(ids)
        print(f"Searching PubMed IDs for year {year} (remaining target: {remaining})...")
        year_ids = _esearch_ids(
            term=term,
            email=email,
            batch_size=batch_size,
            max_records=min(remaining, 9999),
            start_year=year,
            end_year=year,
        )
        ids.extend(year_ids)

    return ids[:max_records]


def _parse_pub_year(article: ET.Element) -> str:
    year = article.find(".//PubDate/Year")
    if year is not None and (year.text or "").strip():
        return (year.text or "").strip()

    medline_date = article.find(".//PubDate/MedlineDate")
    if medline_date is not None:
        text = (medline_date.text or "").strip()
        for token in text.split():
            if token[:4].isdigit():
                return token[:4]

    return "unknown"


def _parse_abstract(article: ET.Element) -> str:
    parts: list[str] = []
    for abstract_text in article.findall(".//Abstract/AbstractText"):
        label = (abstract_text.attrib.get("Label") or "").strip()
        text = _get_text(abstract_text)
        if not text:
            continue
        if label:
            parts.append(f"{label}: {text}")
        else:
            parts.append(text)
    return "\n".join(parts).strip()


def _efetch_records(pmids: list[str], email: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []

    for idx in range(0, len(pmids), 200):
        batch = pmids[idx : idx + 200]
        params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "xml",
            "email": email,
            "tool": "askdocai_importer",
        }

        raw = _request(EFETCH_URL, params)
        root = ET.fromstring(raw)

        for article in root.findall(".//PubmedArticle"):
            pmid = _get_text(article.find(".//PMID"))
            title = _get_text(article.find(".//ArticleTitle"))
            abstract = _parse_abstract(article)

            if not pmid or not title or not abstract:
                continue

            journal = _get_text(article.find(".//Journal/Title"))
            year = _parse_pub_year(article)

            records.append(
                {
                    "id": f"pubmed-{pmid}",
                    "question": title,
                    "answer": abstract,
                    "source": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "updated_at": year,
                    "journal": journal or "unknown",
                    "pmid": pmid,
                    "dataset": "pubmed",
                }
            )

        time.sleep(0.34)

    return records


def _merge_records(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dedup: dict[str, dict[str, Any]] = {}

    for row in existing:
        rid = str(row.get("id") or "")
        if rid:
            dedup[rid] = row
        else:
            key = f"{row.get('question', '')}::{row.get('answer', '')}"
            dedup[key] = row

    for row in incoming:
        rid = str(row.get("id") or "")
        if rid:
            dedup[rid] = row
        else:
            key = f"{row.get('question', '')}::{row.get('answer', '')}"
            dedup[key] = row

    return list(dedup.values())


def main() -> None:
    parser = argparse.ArgumentParser(description="Import PubMed abstracts to AskDocAI JSON format")
    parser.add_argument(
        "--query",
        default=DEFAULT_BROAD_QUERY,
        help="PubMed query. If omitted, uses a broad medical-issues query.",
    )
    parser.add_argument(
        "--email",
        default=os.getenv("NCBI_EMAIL", ""),
        help="Email for NCBI E-utilities. Optional if NCBI_EMAIL env var is set.",
    )
    parser.add_argument("--max-records", type=int, default=5000, help="Maximum records to fetch")
    parser.add_argument("--batch-size", type=int, default=500, help="Esearch page size (<= 10000)")
    parser.add_argument("--start-year", type=int, default=None, help="Optional publication start year")
    parser.add_argument("--end-year", type=int, default=None, help="Optional publication end year")
    parser.add_argument("--output", default="data/medical_data.json", help="Output JSON path")
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing output file with ID-based deduplication",
    )
    args = parser.parse_args()
    email = (args.email or "").strip() or "noreply@example.com"
    if email == "noreply@example.com":
        print(
            "Warning: no email provided. Using fallback 'noreply@example.com'. "
            "For reliable PubMed access, pass --email or set NCBI_EMAIL."
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Searching PubMed IDs...")
    print(f"Using query: {args.query}")
    safe_batch_size = max(1, min(args.batch_size, 10000))
    target_records = max(1, args.max_records)

    if target_records <= 9999:
        ids = _esearch_ids(
            term=args.query,
            email=email,
            batch_size=safe_batch_size,
            max_records=target_records,
            start_year=args.start_year,
            end_year=args.end_year,
        )
    else:
        start_year = args.start_year or 1950
        end_year = args.end_year or datetime.now().year
        if start_year > end_year:
            raise ValueError("start_year cannot be greater than end_year")

        print(
            "Requested more than 9,999 records. Switching to year-chunked retrieval "
            "to bypass the PubMed ESearch pagination cap."
        )
        ids = _esearch_ids_chunked_by_year(
            term=args.query,
            email=email,
            batch_size=safe_batch_size,
            max_records=target_records,
            start_year=start_year,
            end_year=end_year,
        )

    print(f"Found IDs: {len(ids)}")

    if not ids:
        raise ValueError("No PubMed IDs found for the given query.")

    print("Fetching PubMed abstracts...")
    records = _efetch_records(ids, email=email)
    print(f"Parsed records: {len(records)}")

    final_records: list[dict[str, Any]] = records
    if args.append and output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing = json.load(f)
        if not isinstance(existing, list):
            raise ValueError("Existing output file is not a JSON list.")
        final_records = _merge_records(existing, records)
        print(f"Merged total records: {len(final_records)}")

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(final_records, f, ensure_ascii=False, indent=2)

    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()