from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def get_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join("".join(element.itertext()).split())


def find_first_text(root: ET.Element, candidates: Iterable[str]) -> str:
    wanted = {c.lower() for c in candidates}
    for elem in root.iter():
        if local_name(elem.tag).lower() in wanted:
            text = get_text(elem)
            if text:
                return text
    return ""


def parse_medquad_xml(xml_path: Path) -> list[dict[str, str]]:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    base_source = (
        find_first_text(root, ["URL", "Source", "DocumentURL"])
        or f"medquad:{xml_path.name}"
    )

    records: list[dict[str, str]] = []

    for elem in root.iter():
        if local_name(elem.tag).lower() != "qapair":
            continue

        question = ""
        answer = ""

        for child in elem.iter():
            child_name = local_name(child.tag).lower()
            if child_name == "question" and not question:
                question = get_text(child)
            if child_name == "answer" and not answer:
                answer = get_text(child)

        if question and answer:
            records.append(
                {
                    "question": question,
                    "answer": answer,
                    "source": base_source,
                    "updated_at": "unknown",
                }
            )

    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert MedQuAD XML to AskDocAI JSON format")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to MedQuAD directory (containing XML files)",
    )
    parser.add_argument(
        "--output",
        default="data/medical_data.json",
        help="Output JSON path (default: data/medical_data.json)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional max number of records to export (0 = all)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    xml_files = sorted(input_dir.rglob("*.xml"))
    if not xml_files:
        raise FileNotFoundError(f"No XML files found in: {input_dir}")

    all_records: list[dict[str, str]] = []
    seen_pairs: set[tuple[str, str]] = set()

    for xml_file in xml_files:
        try:
            records = parse_medquad_xml(xml_file)
        except ET.ParseError:
            continue

        for record in records:
            key = (record["question"], record["answer"])
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            all_records.append(record)
            if args.limit and len(all_records) >= args.limit:
                break

        if args.limit and len(all_records) >= args.limit:
            break

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    print(f"Parsed XML files: {len(xml_files)}")
    print(f"Exported QA records: {len(all_records)}")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
