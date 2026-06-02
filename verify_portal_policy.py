from __future__ import annotations

import argparse
from datetime import date, datetime
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.portal_registry import (  # noqa: E402
    R_POLICY_LABELS,
    get_effective_portal_policy,
    get_portal_policy_override_path,
    iter_portals,
    write_portal_policy_override_template,
)


def _parse_today(raw: str | None) -> date:
    if not raw:
        return date.today()
    return datetime.strptime(raw, "%Y-%m-%d").date()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify ATK-Pro portal record-mode policy and local override freshness."
    )
    parser.add_argument("--local-policy", help="Path to portal_policy_overrides.json.")
    parser.add_argument("--today", help="Override current date, YYYY-MM-DD.")
    parser.add_argument("--strict", action="store_true", help="Fail when any static portal policy needs re-check.")
    parser.add_argument(
        "--write-template",
        action="store_true",
        help="Write a local portal_policy_overrides.json template and exit.",
    )
    args = parser.parse_args()

    policy_path = Path(args.local_policy) if args.local_policy else get_portal_policy_override_path()
    if args.write_template:
        written = write_portal_policy_override_template(policy_path)
        print(f"Template written: {written}")
        return 0

    today = _parse_today(args.today)
    stale_count = 0

    print(f"Local policy file: {policy_path}")
    if not policy_path.exists():
        print("Local policy file: not present; using registry defaults.")
    else:
        try:
            raw_policy = json.loads(policy_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"ERROR: local policy file is not valid JSON: {exc}")
            return 1
        if not isinstance(raw_policy, dict) or not isinstance(raw_policy.get("portals"), dict):
            print("ERROR: local policy file must contain a top-level 'portals' object.")
            return 1

    for portal in iter_portals():
        policy = get_effective_portal_policy(portal.key, local_policy_path=policy_path, today=today)
        if policy is None:
            continue
        if policy.recheck_due:
            stale_count += 1
        status = "RECHECK" if policy.recheck_due else "OK"
        label = R_POLICY_LABELS.get(policy.record_mode_policy, policy.record_mode_policy)
        checked = policy.policy_checked_at or "per-request"
        print(
            f"{status:7} {portal.key:28} {policy.record_mode_policy:10} "
            f"{checked:12} {policy.policy_source:8} {label}"
        )

    if args.strict and stale_count:
        print(f"ERROR: {stale_count} portal policies need re-check.")
        return 1

    print(f"Portal policies needing re-check: {stale_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
