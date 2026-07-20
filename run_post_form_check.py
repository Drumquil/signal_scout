"""
Run the first-tester post-form validation sequence.

This helper keeps the live onboarding path repeatable without bypassing the
human approval gate in transform_form_response.py.
"""

import argparse
import os
import re
import subprocess
import sys


def run_command(command, env=None, capture=False):
    print(f"\n> {' '.join(command)}")
    completed = subprocess.run(
        command,
        env=env,
        check=False,
        text=True,
        capture_output=capture,
    )
    if capture:
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed.stdout if capture else ""


def validate_args(args):
    if not args.run_scout:
        return
    if args.row is None:
        raise SystemExit("--row is required when --run-scout is used.")
    if not args.target_user_id.strip():
        raise SystemExit("--target-user-id is required when --run-scout is used.")
    try:
        if float(args.request_delay) <= 0:
            raise ValueError
    except ValueError:
        raise SystemExit("--request-delay must be a positive number.")


def extract_preview_user_id(output):
    match = re.search(r"\buser_id will be:\s*([A-Za-z0-9_-]+)", output or "")
    return match.group(1) if match else None


def validate_preview_target(preview_output, target_user_id):
    preview_user_id = extract_preview_user_id(preview_output)
    if not preview_user_id:
        raise SystemExit("Could not read user_id from transform dry-run output.")
    if preview_user_id != target_user_id:
        raise SystemExit(
            f"--target-user-id {target_user_id!r} does not match previewed user_id {preview_user_id!r}."
        )


def main():
    parser = argparse.ArgumentParser(description="Validate a new tester form response.")
    parser.add_argument("--row", type=int, default=None, help="Specific form response row to preview.")
    parser.add_argument(
        "--run-scout",
        action="store_true",
        help="After the dry-run preview, run cattle_scout.py in TEST_MODE=TRUE.",
    )
    parser.add_argument("--max-pages", default="5", help="AuctionsPlus result pages to scan when --run-scout is set.")
    parser.add_argument("--scrape-workers", default="4", help="Detail scrape workers when --run-scout is set.")
    parser.add_argument("--request-delay", default="1", help="Seconds between detail request starts when --run-scout is set.")
    parser.add_argument("--cache-ttl-seconds", default="10800", help="Listing cache TTL when --run-scout is set.")
    parser.add_argument("--target-user-id", default="", help="Optional user_id to evaluate when --run-scout is set.")
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Bypass the listing detail cache when --run-scout is set.",
    )
    args = parser.parse_args()
    validate_args(args)

    python = sys.executable

    run_command([python, "-m", "unittest", "test_transform_form_response_contract.py"])

    transform_command = [python, "transform_form_response.py", "--dry-run"]
    if args.row is not None:
        transform_command.extend(["--row", str(args.row)])
    preview_output = run_command(transform_command, capture=args.run_scout)

    if args.run_scout:
        validate_preview_target(preview_output, args.target_user_id)
        env = os.environ.copy()
        env.update(
            {
                "TEST_MODE": "TRUE",
                "MAX_PAGES": args.max_pages,
                "SCRAPE_WORKERS": args.scrape_workers,
                "REQUEST_DELAY": args.request_delay,
                "LISTING_CACHE_TTL_SECONDS": args.cache_ttl_seconds,
                "LISTING_CACHE_PENDING_TTL_SECONDS": "900",
                "LISTING_CACHE_FILE": ".runtime_cache/listing_detail_cache.json",
                "TARGET_USER_ID": args.target_user_id,
                "FORCE_REFRESH": "TRUE" if args.force_refresh else "FALSE",
                "ENABLE_STOCKPLACE_SOURCE": "FALSE",
                "ENABLE_RMA_SOURCE": "FALSE",
                "ENABLE_AUTHORIZED_NOTICE_SOURCE": "FALSE",
            }
        )
        run_command([python, "cattle_scout.py"], env=env)


if __name__ == "__main__":
    main()
