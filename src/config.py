from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GenerationConfig:
    rows: int
    n_sources: int = 3

    # DaPo+
    duplicate_rate: float = 0.10
    missing_rate: float = 0.03
    typo_rate: float = 0.03
    outdated_rate: float = 0.03
    copy_rate: float = 0.20  # share of rows partially copied from previous source

    seed: int = 42