from __future__ import annotations

import os
from typing import Dict

import pandas as pd
from sqlalchemy import create_engine

from .pollution import GoldStandard


def save_csv_bundle(
    out_dir: str,
    sources: Dict[str, pd.DataFrame],
    integrated: pd.DataFrame,
    gold: GoldStandard,
    quality_df: pd.DataFrame,
) -> None:
    """
    Saves one run as a CSV bundle:
    - sources: S1.csv, S2.csv, ...
    - integrated.csv
    - gold_standard.csv
    - quality_metrics.csv
    """
    os.makedirs(out_dir, exist_ok=True)

    for name, df in sources.items():
        df.to_csv(os.path.join(out_dir, f"{name}.csv"), index=False)

    integrated.to_csv(os.path.join(out_dir, "integrated.csv"), index=False)
    gold.mapping.to_csv(os.path.join(out_dir, "gold_standard.csv"), index=False)
    quality_df.to_csv(os.path.join(out_dir, "quality_metrics.csv"), index=False)


def save_postgres_bundle(
    dsn: str,
    sources: Dict[str, pd.DataFrame],
    integrated: pd.DataFrame,
    gold: GoldStandard,
    quality_df: pd.DataFrame,
) -> None:
    """
    Saves one run into Postgres tables:
    - source_s1, source_s2, ...
    - integrated
    - gold_standard
    - quality_metrics
    """
    engine = create_engine(dsn)

    for name, df in sources.items():
        df.to_sql(f"source_{name.lower()}", engine, if_exists="replace", index=False)

    integrated.to_sql("integrated", engine, if_exists="replace", index=False)
    gold.mapping.to_sql("gold_standard", engine, if_exists="replace", index=False)
    quality_df.to_sql("quality_metrics", engine, if_exists="replace", index=False)