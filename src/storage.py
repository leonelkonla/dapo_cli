from __future__ import annotations

import os
from typing import Dict, Union

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url

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


def _normalize_postgres_dsn(dsn: Union[str, bytes, bytearray]) -> Union[str, URL]:
    """
    Fixes common Windows/psycopg2 DSN encoding issues without changing the CLI:
    - If DSN arrives as bytes -> decode safely (utf-8, fallback cp1252/latin-1).
    - If DSN is a URL (contains ://) -> parse via SQLAlchemy to handle special chars safely.
    """
    # 1) Ensure it's a proper text string
    if isinstance(dsn, (bytes, bytearray)):
        try:
            dsn = dsn.decode("utf-8")
        except UnicodeDecodeError:
            # Windows frequently uses cp1252; latin-1 also works as a safe fallback
            dsn = dsn.decode("cp1252")

    if not isinstance(dsn, str):
        dsn = str(dsn)

    # 2) If it's a URL-style DSN, let SQLAlchemy parse it
    #    (helps with special characters in username/password)
    if "://" in dsn:
        url = make_url(dsn)
        # normalize scheme if someone used "postgres://"
        if url.drivername == "postgres":
            url = url.set(drivername="postgresql")
        return url

    # 3) Otherwise: libpq keyword DSN like "host=... dbname=... user=... password=..."
    return dsn


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
    dsn_norm = _normalize_postgres_dsn(dsn)
    engine = create_engine(dsn_norm)

    for name, df in sources.items():
        df.to_sql(f"source_{name.lower()}", engine, if_exists="replace", index=False)

    integrated.to_sql("integrated", engine, if_exists="replace", index=False)
    gold.mapping.to_sql("gold_standard", engine, if_exists="replace", index=False)
    quality_df.to_sql("quality_metrics", engine, if_exists="replace", index=False)