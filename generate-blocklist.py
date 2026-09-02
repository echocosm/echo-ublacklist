#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from pathlib import Path
import argparse
import dns.resolver
import json
import shutil
import signal
import sys
import time
import urllib.request


def raise_error(_signum: int, _frame: object | None):
    """This handler will raise an error inside gethostbyname"""
    raise OSError


def handle_sigint(signum: int, _frame: object | None):
    print(f"\nCaught Ctrl+C (signal {signum})")
    sys.exit(0)


_ = signal.signal(signal.SIGINT, handle_sigint)


def domain_resolves(domain: str) -> tuple[str, bool]:
    """Return (domain, True/False) depending on whether it resolves."""
    timeout = 1

    try:
        _ = dns.resolver.resolve(domain, "A", lifetime=timeout)
        return domain, True
    except dns.resolver.NXDOMAIN:
        return domain, False
    except dns.resolver.Timeout:
        return domain, False
    except Exception:
        return domain, False


def get_country_domains() -> list[dict[str, str]]:
    """Fetch list of country TLDs from GitHub JSON."""
    url = "https://raw.githubusercontent.com/samayo/country-json/refs/heads/master/src/country-by-domain-tld.json"
    headers = {
        "Accept": "application/json",
    }

    json_data: list[dict[str, str]] = []

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=5) as response:
        raw_body = response.read().decode("utf-8").strip()
        try:
            json_data = json.loads(raw_body)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    return json_data


def generate_ublacklist_entry(domain: str) -> str:
    """Return a uBlacklist rule for the given domain."""
    return f"*://*.{domain}/*"


def main():
    parser = argparse.ArgumentParser(
        prog="generate-blacklist",
        description="Generate uBlacklist rules from one of more base domains",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--domain",
        action="append",
        help="Domain to generate rules for, e.g., pinterest",
        required=True,
    )
    parser.add_argument(
        "-o", "--outfile", default="uBlacklist.txt", help="Output filename"
    )
    args = parser.parse_args()

    json_data = get_country_domains()
    output_file = Path(args.outfile)
    common_tlds = ["com", "edu", "net", "org"]
    to_check = []

    for domain in args.domain:
        domain = domain.split(".")[0]
        for tld in common_tlds:
            to_check.append(f"{domain}.{tld}")

        for country in json_data:
            tld = country.get("tld")
            if tld:
                tld = tld.lstrip(".")
                to_check.append(f"{domain}.{tld}")
                to_check.append(f"{domain}.com.{tld}")

    to_check = sorted(to_check)
    longest = 0
    max_length = 30
    for domain in to_check:
        longest = (
            len(domain)
            if (len(domain) > longest and len(domain) <= max_length)
            else longest
        )

    term_width = shutil.get_terminal_size((80, 25)).columns
    bar_width = max(80, term_width - 10)
    results = {}
    start = time.time()

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(domain_resolves, d): d for d in to_check}
        with tqdm(total=len(to_check), ncols=bar_width, leave=True) as pbar:
            for future in as_completed(futures):
                d, resolves = future.result()
                results[d] = resolves
                pbar.set_description(f"Checking {d:<{longest}.{longest}}")
                ok = sum(results.values())
                pbar.set_postfix(ok=ok, fail=len(results) - ok)
                pbar.update(1)

    # Build blacklist entries for domains that resolved
    resolved_domains = [d for d, ok in results.items() if ok]
    blacklist_entries = [generate_ublacklist_entry(d) for d in resolved_domains]

    # Write them to a file, one per line (no blank lines)
    output_file.write_text("\n".join(sorted(blacklist_entries)), encoding="utf-8")

    print(f"\nDone in {time.time() - start:.2f}s")
    print(f"{len(resolved_domains)} domains resolved.")
    print(f"uBlacklist file saved to: {output_file}")


if __name__ == "__main__":
    main()
