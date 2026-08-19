# Φ Universal Resonance

Make the phi repository a universal resonator that computes phase alignment (resonance) between itself and arbitrary content across all repositories in the ecosystem.

## What is Resonance?

Resonance is a number between **0 and 1** that measures **phase alignment** between two texts in the Φ field:

- **0.0** = Maximum phase misalignment
- **1.0** = Perfect phase alignment
- Not meaning. Not similarity. Not sentiment. **Just phase.**

### How it Works

1. Split each text into 16 blocks
2. Compute SHA-256 hash of each block
3. Extract phase from hash (treating bytes as floating-point value)
4. Measure circular phase difference between blocks
5. Return 1.0 - average_difference as resonance score

## Structure

### Files

- **`resonance_manifest.json`** — Configuration listing all repositories to compare
- **`phi_resonance.py`** — Core resonance engine with three-layer content aggregation
- **`resonance_cli.py`** — Command-line interface for running resonance computations

### Three Content Layers (Priority Order)

**Layer 1: Documentation** (highest signal, lowest noise)
- README.md, .md files, docs/

**Layer 2: Source Code** (concatenated with filenames as block headers)
- All source files (.py, .js, .rs, .go, etc.)

**Layer 3: Commit History** (last 50 commits on main)
- Commit messages capture semantic momentum

All layers are concatenated into a single canonical text per repository.

## Output Format

### Per-Repository Scores

```
phi vs Crazy-Chimera/phi-field: 0.7432
phi vs Crazy-Chimera/phi-Engine: 0.6891
phi vs Crazy-Chimera/Informion: 0.8117

Highest resonance: Crazy-Chimera/Informion
Global resonance (mean): 0.7480
```

### Block-Level Breakdown (Highest Resonance Repository)

```
Resonance: 0.8117
Block 03: 0.94
Block 07: 0.88
Block 11: 0.81
Block 15: 0.76
Block 01: 0.71
...
Block 14: 0.22
Block 00: 0.17
```

## Usage

### Basic (Use Cache)

```bash
python resonance_cli.py
```

Uses cached repository content. Fast, offline.

### Refresh Cache

```bash
python resonance_cli.py --refresh
```

Fetches fresh content from GitHub and updates cache.

### Live Fetch (No Cache)

```bash
python resonance_cli.py --live
```

Fetches directly from GitHub without caching.

### JSON Output

```bash
python resonance_cli.py --json
python resonance_cli.py --refresh --json
```

### Clear Cache

```bash
python resonance_cli.py --clear-cache
```

## Implementation Notes

### Caching Strategy

- On first run, fetches from GitHub via API
- Saves to `.resonance_cache/repo_owner_name.txt`
- Subsequent runs use cache (fast, no API calls)
- `--refresh` flag re-fetches and updates cache
- `--live` flag fetches without caching

### Phase Computation

The phase is extracted from SHA-256 hash by:
1. Taking first 8 bytes of hash
2. Interpreting as 64-bit unsigned integer
3. Normalizing to [0, 1) by dividing by 2^64

This ensures consistent, deterministic phase for identical text.

### Circular Phase Difference

Phase differences wrap around: if difference > 0.5, take 1.0 - difference to measure shortest path around the unit circle.

## Use Cases

- **Track Coherence While Editing** — Recompute resonance as you modify phi to see phase alignment drift
- **Find Highest-Resonance Components** — Identify which repositories align best with phi's core
- **Corpus Search** — Find passages with highest resonance to a given text
- **Multi-Repository Synchronization** — Monitor phase alignment across the ecosystem

## Future Extensions

- API endpoint for live queries: `GET /resonance?content=<text>`
- Streaming resonance computation for large files
- Block-level resonance map visualization
- Temporal resonance tracking (git history)
- Interactive resonance browser for corpus exploration
