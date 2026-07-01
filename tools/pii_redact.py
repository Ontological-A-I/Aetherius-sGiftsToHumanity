"""
Streaming PII redactor for Aetherius log files.
Reads line-by-line (flat memory footprint), replaces PII with [REDACTED],
writes a clean copy. Original file is never modified.
"""
import re
import json
import os
import sys
import argparse

PATTERNS = {
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
    "phone": re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
    "ip_address": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    "street_address": re.compile(
        r'\b\d{1,5}\s+\w+(\s\w+)*\s(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b',
        re.IGNORECASE
    ),
}

# These are known-safe patterns that the regex may false-positive on
SAFE_PATTERNS = re.compile(
    r'(\b(?:127|192|10)\.\d+\.\d+\.\d+\b)'  # localhost / private IP ranges
)

def redact_text(text: str) -> tuple[str, bool]:
    changed = False
    for name, pattern in PATTERNS.items():
        def replacer(m):
            nonlocal changed
            val = m.group(0)
            # Skip if already looks redacted or is a safe pattern
            if SAFE_PATTERNS.match(val):
                return val
            changed = True
            return "[REDACTED]"
        text = pattern.sub(replacer, text)
    return text, changed


def redact_jsonl(input_path: str, output_path: str) -> dict:
    stats = {"lines": 0, "lines_modified": 0, "total_replacements": 0}
    with open(input_path, "r", encoding="utf-8", errors="ignore") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            raw = line.strip()
            if not raw:
                fout.write(line)
                continue
            stats["lines"] += 1
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                fout.write(line)
                continue

            modified = False
            for field in ["redacted_text", "content", "text", "message", "response"]:
                if field in obj and isinstance(obj[field], str):
                    cleaned, changed = redact_text(obj[field])
                    if changed:
                        obj[field] = cleaned
                        obj["redaction_performed"] = True
                        modified = True
                        stats["total_replacements"] += 1

            if modified:
                stats["lines_modified"] += 1

            fout.write(json.dumps(obj) + "\n")
    return stats


def redact_json(input_path: str, output_path: str) -> dict:
    """Redacts PII from arbitrary JSON (non-JSONL) by converting to string and back."""
    stats = {"replacements": 0}
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    def replacer(m):
        stats["replacements"] += 1
        return "[REDACTED]"

    for name, pattern in PATTERNS.items():
        raw = pattern.sub(replacer, raw)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(raw)
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--format", choices=["jsonl", "json"], default="jsonl")
    args = parser.parse_args()

    if args.format == "jsonl":
        stats = redact_jsonl(args.input, args.output)
    else:
        stats = redact_json(args.input, args.output)

    print(json.dumps(stats, indent=2))
