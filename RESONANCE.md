# Φ‑TRT Temporal Resonance Technology

A universal resonator that computes phase alignment between the phi repository and any arbitrary content—poems, theories, repositories, ideas, names.

## What is Resonance?

Resonance is a number between **0 and 1** that measures **phase alignment** in the Φ field:

- **1.0** = Perfect phase alignment (maximum resonance)
- **0.5** = Random phase difference
- **0.0** = Maximum misalignment

Resonance is **not** semantic similarity, sentiment, or textual meaning. It is pure **phase alignment** derived from SHA-256 spectral fingerprints.

### How It Works

1. Split each text into 16 blocks
2. Compute SHA-256 hash of each block → extract phase ∈ [0, 2π)
3. Measure circular phase difference between corresponding blocks
4. Return 1.0 - (average difference / π) as the resonance score

## Usage

### Basic Resonance Computation

```bash
# Compare phi against all repos in resonance_manifest.json
python resonance_cli.py

# Machine-readable output (JSON)
python resonance_cli.py --json

# Compare against a single repository
python resonance_cli.py --repo Crazy-Chimera/phi-resonance
```

### Cache Management

```bash
# Force live GitHub fetch (no cache)
python resonance_cli.py --live

# Clear cache and re-fetch all content
python resonance_cli.py --refresh
```

### Custom Manifest

```bash
python resonance_cli.py --manifest custom_manifest.json
```

## Repository Configuration

Edit `resonance_manifest.json` to add or remove repositories:

```json
{
  "repositories": [
    "Crazy-Chimera/phi",
    "Crazy-Chimera/phi-resonance",
    "Crazy-Chimera/loopos",
    "Crazy-Chimera/synaphe",
    "Crazy-Chimera/melanie"
  ]
}
```

## Direct API Usage

```python
from resonance import universal_resonance, block_map

# Compute resonance between two text strings
score = universal_resonance("text A", "text B")
print(f"Resonance: {score:.4f}")

# Get per-block resonance map (highest to lowest)
blocks = block_map("text A", "text B")
for block_idx, res in blocks:
    print(f"Block {block_idx:02d}: {res:.2f}")
```

## Content Layers

When fetching repository content, resonance aggregates three layers (priority order):

1. **Documentation** — README.md and top-level .md files
2. **Source Code** — .py, .js, .rs, .go, and other source files
3. **Commit History** — Last 50 commit messages from main branch

All layers are concatenated into a canonical text fingerprint.

## Cache

On first run, repository content is fetched from GitHub and cached in `.resonance_cache/`. Subsequent runs use the cache (fast, offline).

Use `--refresh` to update the cache.

## Φ

The phi repository is now a universal resonator. It can measure phase alignment with anything.
