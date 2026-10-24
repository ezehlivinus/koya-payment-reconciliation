#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime
from decimal import Decimal


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_amount(value):
    # Some exports format amounts as strings with thousands separators, e.g. "4,804.15".
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return Decimal(str(value))


# Only the latest attempt (by ts) for each txn_id counts.
latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or not event.get("txn_id"):
            continue
        txn_id = event["txn_id"]
        ts = parse_ts(event["ts"])
        if txn_id not in latest or ts > latest[txn_id][0]:
            latest[txn_id] = (ts, event)

total = Decimal(0)
count = 0

for _, event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
