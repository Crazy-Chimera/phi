#!/usr/bin/env python3
"""
Φ‑TRT Resonance CLI – Compare the phi repository against all repos
in the manifest.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from resonance import compare_all, load_manifest


def print_report(report: dict) -> None:
    """Print a human-readable resonance report."""
    print("Resonance Report")
    print("=================")
    print()

    scores = report["scores"]
    highest = report["highest"]
    global_mean = report["global_mean"]

    for repo, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        marker = "  ★ HIGHEST" if repo == highest else ""
        print(f"phi vs {repo}: {score:.4f}{marker}")

    print()
    print(f"Global resonance (mean): {global_mean:.4f}")

    if report["block_map"]:
        print()
        print(f"Block map for highest resonance (phi vs {highest}):")
        for block_idx, res in report["block_map"]:
            print(f"  Block {block_idx:02d}: {res:.2f}")


def print_json(report: dict) -> None:
    """Print machine-readable JSON."""
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Compute resonance between phi and other repositories."
    )
    parser.add_argument("--live", action="store_true",
                        help="Fetch live data from GitHub (no cache).")
    parser.add_argument("--refresh", action="store_true",
                        help="Clear cache and re-fetch all content.")
    parser.add_argument("--repo", type=str, default=None,
                        help="Compare against a single repository.")
    parser.add_argument("--json", action="store_true",
                        help="Output machine-readable JSON.")
    parser.add_argument("--manifest", type=str, default=None,
                        help="Path to a custom manifest JSON file.")
    args = parser.parse_args()

    # Load manifest
    repos = load_manifest(args.manifest) if args.manifest else load_manifest()

    # Single repo mode
    if args.repo:
        repos = [args.repo]

    report = compare_all(
        manifest_path=args.manifest,
        live=args.live,
        refresh=args.refresh,
    )

    if args.json:
        print_json(report)
    else:
        print_report(report)


if __name__ == "__main__":
    main()
