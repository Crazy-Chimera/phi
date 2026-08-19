"""
Universal Resonance Framework for Φ Field

Computes phase alignment (resonance) between the phi repository
and all other repositories in the Φ ecosystem.

Core resonance function already exists:
  def universal_resonance(content_a: str, content_b: str) -> float

This module extends it with multi-repository folding and reporting.
"""

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class BlockResonance:
    """Resonance score for a single block."""
    block_index: int
    score: float

    def __repr__(self) -> str:
        return f"Block {self.block_index:02d}: {self.score:.2f}"


@dataclass
class RepositoryResonance:
    """Complete resonance analysis for one repository."""
    repository: str
    overall_score: float
    block_scores: List[BlockResonance]

    @property
    def top_blocks(self) -> List[BlockResonance]:
        """Return blocks sorted by resonance (highest first)."""
        return sorted(self.block_scores, key=lambda b: b.score, reverse=True)

    def to_dict(self) -> dict:
        return {
            "repository": self.repository,
            "overall_score": self.overall_score,
            "block_scores": [asdict(b) for b in self.block_scores]
        }


@dataclass
class GlobalResonance:
    """Aggregate resonance across all repositories."""
    repositories: List[RepositoryResonance]
    global_mean: float
    highest_resonance_repo: str

    @property
    def sorted_by_resonance(self) -> List[RepositoryResonance]:
        """Return repositories sorted by resonance (highest first)."""
        return sorted(self.repositories, key=lambda r: r.overall_score, reverse=True)

    def to_dict(self) -> dict:
        return {
            "global_mean": self.global_mean,
            "highest_resonance": self.highest_resonance_repo,
            "repositories": [r.to_dict() for r in self.repositories]
        }


def universal_resonance(content_a: str, content_b: str) -> Tuple[float, List[BlockResonance]]:
    """
    Compute phase alignment resonance between two text blocks.

    Args:
        content_a: First text block
        content_b: Second text block

    Returns:
        Tuple of (overall_resonance_score, list_of_block_resonances)
        where overall_resonance_score is between 0 and 1,
        and block_resonances is a list of per-block scores.

    The function splits each text into 16 blocks, computes the phase
    of each block from its SHA-256 hash, measures average phase difference,
    and returns 1.0 - difference as the resonance score.
    """
    def compute_phase(text: str) -> float:
        """Compute phase from SHA-256 hash of text."""
        h = hashlib.sha256(text.encode()).digest()
        # Interpret first 8 bytes as float in [0, 1)
        phase = int.from_bytes(h[:8], 'big') / (2**64)
        return phase

    def split_into_blocks(text: str, num_blocks: int = 16) -> List[str]:
        """Split text into N approximately equal blocks."""
        lines = text.split('\n')
        lines_per_block = max(1, len(lines) // num_blocks)
        blocks = []
        for i in range(num_blocks):
            start = i * lines_per_block
            end = start + lines_per_block if i < num_blocks - 1 else len(lines)
            block_text = '\n'.join(lines[start:end])
            blocks.append(block_text)
        return blocks

    blocks_a = split_into_blocks(content_a, 16)
    blocks_b = split_into_blocks(content_b, 16)

    block_resonances = []
    total_diff = 0.0

    for i, (block_a, block_b) in enumerate(zip(blocks_a, blocks_b)):
        phase_a = compute_phase(block_a)
        phase_b = compute_phase(block_b)
        # Circular phase difference (shortest path around unit circle)
        diff = abs(phase_a - phase_b)
        diff = min(diff, 1.0 - diff)
        resonance = 1.0 - diff
        block_resonances.append(BlockResonance(block_index=i, score=resonance))
        total_diff += diff

    overall_resonance = 1.0 - (total_diff / len(blocks_a))
    return overall_resonance, block_resonances


class ResonanceCache:
    """Manages caching of repository content."""

    def __init__(self, cache_dir: str = ".resonance_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def get_cache_path(self, repo: str) -> Path:
        """Return cache file path for repository."""
        safe_name = repo.replace('/', '_')
        return self.cache_dir / f"{safe_name}.txt"

    def has_cached(self, repo: str) -> bool:
        """Check if repository content is cached."""
        return self.get_cache_path(repo).exists()

    def load_cached(self, repo: str) -> str:
        """Load cached content for repository."""
        path = self.get_cache_path(repo)
        if path.exists():
            return path.read_text(encoding='utf-8')
        return ""

    def save_cache(self, repo: str, content: str) -> None:
        """Save repository content to cache."""
        path = self.get_cache_path(repo)
        path.write_text(content, encoding='utf-8')

    def clear_cache(self) -> None:
        """Clear all cached files."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(exist_ok=True)


class RepositoryContentFetcher:
    """Fetches and combines content from repositories in priority order."""

    def __init__(self, cache: ResonanceCache, use_cache: bool = True, use_live: bool = False):
        self.cache = cache
        self.use_cache = use_cache
        self.use_live = use_live

    def fetch_repository(self, owner: str, repo: str) -> str:
        """
        Fetch repository content from three layers.

        Priority:
        1. README and top-level documentation
        2. Source code files with filenames as headers
        3. Commit messages from last 50 commits on main

        Returns: Concatenated canonical text for repository.
        """
        repo_nwo = f"{owner}/{repo}"

        # Check cache first (unless --live is set)
        if self.use_cache and not self.use_live and self.cache.has_cached(repo_nwo):
            return self.cache.load_cached(repo_nwo)

        content_parts = []

        # Layer 1: README and documentation
        readme_content = self._fetch_readme(owner, repo)
        if readme_content:
            content_parts.append(f"=== DOCUMENTATION ===\n{readme_content}\n")

        # Layer 2: Source code files
        source_content = self._fetch_source_files(owner, repo)
        if source_content:
            content_parts.append(f"=== SOURCE CODE ===\n{source_content}\n")

        # Layer 3: Commit messages (last 50 on main)
        commits_content = self._fetch_commit_messages(owner, repo)
        if commits_content:
            content_parts.append(f"=== COMMIT HISTORY ===\n{commits_content}\n")

        canonical = ''.join(content_parts)

        # Cache the result
        self.cache.save_cache(repo_nwo, canonical)

        return canonical

    def _fetch_readme(self, owner: str, repo: str) -> str:
        """Fetch README.md or similar documentation files."""
        # In a real implementation, use GitHub API to fetch README
        # For now, return placeholder that would be filled by API
        return f"README content for {owner}/{repo}"

    def _fetch_source_files(self, owner: str, repo: str) -> str:
        """Fetch and concatenate source code files."""
        # In a real implementation, use GitHub API to list and fetch files
        # Filter by common source extensions and concatenate with filenames as headers
        return f"Source code for {owner}/{repo}"

    def _fetch_commit_messages(self, owner: str, repo: str, limit: int = 50) -> str:
        """Fetch commit messages from the last N commits on main."""
        # In a real implementation, use GitHub API to fetch commit log
        return f"Commit messages for {owner}/{repo}"


def fold_repositories_into_phi(
    manifest_path: str = "resonance_manifest.json",
    cache_dir: str = ".resonance_cache",
    use_cache: bool = True,
    use_live: bool = False
) -> GlobalResonance:
    """
    Compute resonance between phi repository and all configured repositories.

    Args:
        manifest_path: Path to resonance_manifest.json
        cache_dir: Directory for caching repository content
        use_cache: Use cached content if available (default True)
        use_live: Force live GitHub API fetch (overrides cache)

    Returns:
        GlobalResonance object with per-repo and aggregate scores.
    """
    # Load manifest
    if not Path(manifest_path).exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_path) as f:
        manifest = json.load(f)

    repos = manifest.get("repositories", [])
    if not repos:
        raise ValueError("No repositories in manifest")

    # Initialize cache and fetcher
    cache = ResonanceCache(manifest.get("cache_dir", cache_dir))
    fetcher = RepositoryContentFetcher(cache, use_cache=use_cache, use_live=use_live)

    # Fetch phi content (first repo is typically phi itself)
    phi_content = fetcher.fetch_repository("Crazy-Chimera", "phi")

    # Compute resonance for each repository against phi
    repo_resonances = []
    for repo_nwo in repos:
        owner, repo = repo_nwo.split('/')
        repo_content = fetcher.fetch_repository(owner, repo)

        overall_score, block_scores = universal_resonance(phi_content, repo_content)
        repo_res = RepositoryResonance(
            repository=repo_nwo,
            overall_score=overall_score,
            block_scores=block_scores
        )
        repo_resonances.append(repo_res)

    # Compute global statistics
    scores = [r.overall_score for r in repo_resonances]
    global_mean = sum(scores) / len(scores) if scores else 0.0
    highest_repo = max(repo_resonances, key=lambda r: r.overall_score).repository

    return GlobalResonance(
        repositories=repo_resonances,
        global_mean=global_mean,
        highest_resonance_repo=highest_repo
    )


def format_resonance_report(resonance: GlobalResonance) -> str:
    """Format GlobalResonance as human-readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append("Φ UNIVERSAL RESONANCE REPORT")
    lines.append("=" * 70)
    lines.append("")

    # Per-repository scores
    lines.append("REPOSITORY RESONANCE SCORES")
    lines.append("-" * 70)
    for repo in resonance.sorted_by_resonance:
        lines.append(f"{repo.repository}: {repo.overall_score:.4f}")
    lines.append("")

    # Global statistics
    lines.append("AGGREGATE STATISTICS")
    lines.append("-" * 70)
    lines.append(f"Global Resonance (mean): {resonance.global_mean:.4f}")
    lines.append(f"Highest Resonance: {resonance.highest_resonance_repo}")
    lines.append("")

    # Block-level detail for highest resonance repo
    highest = resonance.sorted_by_resonance[0]
    lines.append(f"DETAILED BLOCKS: {highest.repository}")
    lines.append("-" * 70)
    for block in highest.top_blocks[:8]:  # Top 8 blocks
        lines.append(f"{block}")
    if len(highest.top_blocks) > 8:
        lines.append(f"... and {len(highest.top_blocks) - 8} more blocks")
    lines.append("")
    lines.append("=" * 70)

    return '\n'.join(lines)


if __name__ == "__main__":
    import sys

    # Example usage with optional flags
    use_cache = "--refresh" not in sys.argv
    use_live = "--live" in sys.argv

    print("Folding repositories into Φ field...")
    resonance = fold_repositories_into_phi(use_cache=use_cache, use_live=use_live)

    print(format_resonance_report(resonance))

    # Save detailed results to JSON
    with open(".resonance_cache/results.json", "w") as f:
        json.dump(resonance.to_dict(), f, indent=2)
    print(f"\nDetailed results saved to .resonance_cache/results.json")
