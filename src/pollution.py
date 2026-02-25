from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Tuple

import pandas as pd

from .config import GenerationConfig
from .schemas import DatasetSchema


@dataclass
class GoldStandard:
    # maps each source record_id to the underlying entity_id
    mapping: pd.DataFrame  # columns: source, record_id, entity_id


def _typo(s: str, rnd: random.Random) -> str:
    if not s:
        return s
    pos = rnd.randrange(0, len(s))
    ch = chr(rnd.randrange(97, 123))
    return s[:pos] + ch + s[pos + 1 :]


def build_history(clean: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Minimal history: t0 (old), t1 (new)
    t0 = clean.copy()
    t1 = clean.copy()

    # Slightly update first text-like column to enable outdated values
    text_cols = [c for c in t1.columns if t1[c].dtype == "object" and c.lower() != "entity_id"]
    if text_cols:
        c0 = text_cols[0]
        mask = (t1.index % 10 == 0)
        t1.loc[mask, c0] = t1.loc[mask, c0].astype(str) + " (upd)"
    return t0, t1


def _apply_schema_heterogeneity(df: pd.DataFrame, variant: str) -> pd.DataFrame:
    out = df.copy()
    if variant == "camel":
        # snake_case -> camelCase
        def to_camel(c: str) -> str:
            parts = c.split("_")
            return parts[0] + "".join(p.title() for p in parts[1:])

        out.columns = [to_camel(c) for c in out.columns]
    elif variant == "upper":
        out.columns = [c.upper() for c in out.columns]
    # else: keep snake
    return out


def _pollute_values(df: pd.DataFrame, cfg: GenerationConfig, rnd: random.Random) -> pd.DataFrame:
    out = df.copy()

    for col in out.columns:
        # missing
        m_mask = out.index.to_series().apply(lambda _: rnd.random() < cfg.missing_rate)
        out.loc[m_mask, col] = None

        # typos only on strings
        if out[col].dtype == "object":
            t_mask = out.index.to_series().apply(lambda _: rnd.random() < cfg.typo_rate)
            out.loc[t_mask, col] = out.loc[t_mask, col].astype(str).apply(lambda x: _typo(x, rnd))

    return out


def _inject_duplicates(df: pd.DataFrame, cfg: GenerationConfig, rnd: random.Random) -> pd.DataFrame:
    base = df.copy().reset_index(drop=True)
    n_dup = int(len(base) * cfg.duplicate_rate)
    if n_dup <= 0:
        return base

    dup = base.sample(n_dup, random_state=rnd.randint(0, 10_000)).copy()

    # small divergence
    for col in dup.columns:
        if dup[col].dtype == "object":
            mask = dup.index.to_series().apply(lambda _: rnd.random() < 0.4)
            dup.loc[mask, col] = dup.loc[mask, col].astype(str) + " "
    return pd.concat([base, dup], ignore_index=True)


def _norm_col(s: str) -> str:
    # robust matching across snake_case / camelCase / UPPER
    return s.strip().lower().replace("_", "")


def create_sources(
    schema: DatasetSchema,
    clean: pd.DataFrame,
    config: GenerationConfig,
) -> Tuple[Dict[str, pd.DataFrame], GoldStandard]:
    rnd = random.Random(config.seed)

    t0, t1 = build_history(clean)

    sources: Dict[str, pd.DataFrame] = {}
    gold_rows = []

    variants = ["snake", "camel", "upper"]
    target = _norm_col(schema.primary_entity_id)

    for i in range(config.n_sources):
        source_name = f"S{i+1}"

        # start from latest snapshot
        base = t1.copy()

        # outdated values: swap some rows back to t0
        if config.outdated_rate > 0:
            o_mask = base.index.to_series().apply(lambda _: rnd.random() < config.outdated_rate)
            base.loc[o_mask, :] = t0.loc[o_mask, :].values

        # copying (simplified)
        if i > 0 and config.copy_rate > 0 and f"S{i}" in sources:
            donor = sources[f"S{i}"].copy()
            donor = donor.sample(frac=min(0.3, config.copy_rate), random_state=config.seed)

            # if donor is already renamed, skip copying to keep it minimal and safe
            # (we keep copying only in safe scenarios)
            if set(map(_norm_col, donor.columns)) == set(map(_norm_col, base.columns)):
                # try to align by normalized names
                donor.columns = base.columns
                base = pd.concat([base, donor], ignore_index=True)

        # heterogeneity (rename)
        variant = variants[i % len(variants)]
        if variant == "snake":
            represented = base.copy()
        else:
            represented = _apply_schema_heterogeneity(base, variant)

        # pollution + duplicates
        polluted = _pollute_values(represented, config, rnd)
        with_dups = _inject_duplicates(polluted, config, rnd)

        # add record_id
        with_dups = with_dups.reset_index(drop=True)
        with_dups["record_id"] = [f"{source_name}-{k:09d}" for k in range(len(with_dups))]

        # Find entity-id column robustly (snake/camel/upper)
        entity_col = None
        for c in with_dups.columns:
            if _norm_col(c) == target:
                entity_col = c
                break
        if entity_col is None:
            raise ValueError(
                f"entity_id column not found after heterogeneity transformation. "
                f"Expected something like '{schema.primary_entity_id}'. "
                f"Available columns: {list(with_dups.columns)}"
            )

        gold = pd.DataFrame(
            {
                "source": source_name,
                "record_id": with_dups["record_id"],
                "entity_id": with_dups[entity_col],
            }
        )
        gold_rows.append(gold)

        sources[source_name] = with_dups

    gold_df = pd.concat(gold_rows, ignore_index=True)
    return sources, GoldStandard(mapping=gold_df)