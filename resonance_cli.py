#!/usr/bin/env python3
"""
Φ Resonance CLI Tool

Compute and display universal resonance between phi repository
and all configured repositories in the ecosystem.

Usage:
    python resonance_cli.py                 # Use cache
    python resonance_cli.py --refresh       # Refresh cache from GitHub
    python resonance_cli.py --live          # Fetch live (no cache)
    python resonance_cli.py --json          # Output JSON instead of report
"""

import json
import sys
from pathlib import Path
from phi_resonance import (
    fold_repositories_into_phi,
    format_resonance_report,
    ResonanceCache
)


def main():
    # Parse arguments
    use_cache = "--refresh" not in sys.argv and "--live" not in sys.argv
    use_live = "--live" in sys.argv
    output_json = "--json" in sys.argv
    clear_cache = "--clear-cache" in sys.argv

    # Handle cache clearing
    if clear_cache:
        cache = ResonanceCache()
        cache.clear_cache()
        print("Cache cleared.")
        return

    try:
        print("🌀 Computing Φ resonance across repositories...")
        print()

        resonance = fold_repositories_into_phi(
            use_cache=use_cache,
            use_live=use_live
        )

        if output_json:
            # Output JSON format
            print(json.dumps(resonance.to_dict(), indent=2))
        else:
            # Output human-readable report
            print(format_resonance_report(resonance))

        # Print cache status
        print()
        if use_cache:
            print("✓ Results cached at .resonance_cache/")
            print("  Use --refresh to update from GitHub")
            print("  Use --live to fetch without caching")
        elif use_live:
            print("✓ Results fetched live from GitHub")
            print("  Use --refresh to save to cache")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
