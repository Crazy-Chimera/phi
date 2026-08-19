"""
Φ‑TRT Universal Resonator – Pure functions.

Computes resonance between any two text contents, and between
the phi repository and any set of external repositories.
"""
import hashlib
import math
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Core resonance functions
# ---------------------------------------------------------------------------

def phase_of(content: str) -> float:
    """
    The phase of any content is derived from its SHA-256 hash.
    Phase is in the range [0, 2π).
    """
    h = hashlib.sha256(content.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF * 2 * math.pi


def spectral_components(content: str, n: int = 16) -> List[float]:
    """
    Split content into n blocks and compute the phase of each block.
    Returns a list of phases.
    """
    if not content:
        return [0.0] * n
    block_size = max(1, len(content) // n)
    phases = []
    for i in range(n):
        block = content[i * block_size:(i + 1) * block_size]
        phases.append(phase_of(block))
    return phases


def difference(a: List[float], b: List[float]) -> float:
    """
    Compute the total phase difference between two spectral fingerprints.
    Returns a value in [0, 1], where 0 is perfect alignment.
    """
    if len(a) != len(b):
        raise ValueError("Spectral fingerprints must have the same length")
    total = 0.0
    for pa, pb in zip(a, b):
        diff = abs(pa - pb) % (2 * math.pi)
        if diff > math.pi:
            diff = 2 * math.pi - diff
        total += diff / math.pi
    return total / len(a)


def universal_resonance(content_a: str, content_b: str) -> float:
    """
    Compute resonance between any two arbitrary text contents.
    Returns a value in [0, 1], where 1 is perfect resonance.
    """
    sa = spectral_components(content_a)
    sb = spectral_components(content_b)
    return 1.0 - difference(sa, sb)


def block_map(content_a: str, content_b: str, n: int = 16) -> List[Tuple[int, float]]:
    """
    Compute per-block resonance between two contents.
    Returns a list of (block_index, resonance) sorted from highest to lowest.
    """
    sa = spectral_components(content_a, n)
    sb = spectral_components(content_b, n)
    results = []
    for i, (pa, pb) in enumerate(zip(sa, sb)):
        diff = abs(pa - pb) % (2 * math.pi)
        if diff > math.pi:
            diff = 2 * math.pi - diff
        results.append((i, 1.0 - (diff / math.pi)))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Repository content fetching and caching
# ---------------------------------------------------------------------------

CACHE_DIR = Path(__file__).parent / ".resonance_cache"


def load_manifest(path: str = "resonance_manifest.json") -> List[str]:
    """Load the list of repositories from the manifest file."""
    manifest_path = Path(path)
    if not manifest_path.exists():
        # Fallback to default path relative to this file
        manifest_path = Path(__file__).parent / "resonance_manifest.json"
    with open(manifest_path, "r") as f:
        data = json.load(f)
    return data.get("repositories", [])


def fetch_repo_content(repo: str, cache: bool = True) -> str:
    """
    Fetch the canonical text of a repository by cloning it (or using cache).

    Priority of content:
      1. README.md and top-level documentation
      2. Source code files
      3. Commit messages (last 50)
    """
    cache_path = CACHE_DIR / (repo.replace("/", "__") + ".txt")
    if cache and cache_path.exists():
        return cache_path.read_text(encoding="utf-8", errors="ignore")

    # Clone shallowly into a temporary directory
    tmp_dir = CACHE_DIR / "tmp" / repo.replace("/", "__")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    clone_cmd = ["git", "clone", "--depth", "1",
                 f"https://github.com/{repo}.git", str(tmp_dir)]
    subprocess.run(clone_cmd, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    content_parts = []

    # 1. README and docs
    for fname in ["README.md", "README", "readme.md", "readme"]:
        fpath = tmp_dir / fname
        if fpath.exists():
            content_parts.append(f"=== {fname} ===\n")
            content_parts.append(fpath.read_text(encoding="utf-8", errors="ignore"))

    # 2. Source code
    for fpath in sorted(tmp_dir.rglob("*")):
        if not fpath.is_file():
            continue
        if fpath.suffix in {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml"}:
            if fpath.name in {"README.md", "readme.md"}:
                continue
            if ".git" in fpath.parts:
                continue
            content_parts.append(f"=== {fpath.name} ===\n")
            content_parts.append(fpath.read_text(encoding="utf-8", errors="ignore"))

    # 3. Commit messages
    log_cmd = ["git", "-C", str(tmp_dir), "log", "--oneline", "-50"]
    result = subprocess.run(log_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        content_parts.append("=== commit_messages ===\n")
        content_parts.append(result.stdout)

    canonical = "\n".join(content_parts)

    if cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(canonical, encoding="utf-8", errors="ignore")

    return canonical


def phi_content() -> str:
    """
    Get the canonical text of the phi repository itself.
    Uses local files when run inside the repository; otherwise clones.
    """
    # If we're inside the phi repo, read local files
    local_root = Path(__file__).parent
    if (local_root / ".git").exists() or (local_root / "resonance.py").exists():
        return fetch_repo_content("Crazy-Chimera/phi", cache=False)
    return fetch_repo_content("Crazy-Chimera/phi", cache=True)


def compare_all(manifest_path: str = None,
                live: bool = False,
                refresh: bool = False) -> Dict:
    """
    Compare phi against all repositories in the manifest.
    Returns per-repo scores and block map for highest.
    """
    if refresh:
        import shutil
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)

    repos = load_manifest(manifest_path) if manifest_path else load_manifest()
    phi_text = phi_content()
    results = {}

    for repo in repos:
        repo_text = fetch_repo_content(repo, cache=not live)
        score = universal_resonance(phi_text, repo_text)
        results[repo] = score

    # Find highest
    highest_repo = max(results, key=results.get) if results else None
    block_map_data = None
    if highest_repo:
        highest_text = fetch_repo_content(highest_repo, cache=not live)
        block_map_data = block_map(phi_text, highest_text)

    global_mean = sum(results.values()) / len(results) if results else 0.0

    return {
        "scores": results,
        "highest": highest_repo,
        "global_mean": global_mean,
        "block_map": block_map_data,
    }
