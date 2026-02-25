from __future__ import annotations

from typing import Dict
import pandas as pd


def normalize_strings(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.select_dtypes(include="object").columns:
        out[col] = out[col].astype(str).str.strip()
    return out


def fill_nulls(df: pd.DataFrame) -> pd.DataFrame:
    return df.fillna("UNKNOWN")


def integrate_sources(sources: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    frames = []
    for sname, df in sources.items():
        tmp = df.copy()
        tmp["source"] = sname
        frames.append(tmp)
    return pd.concat(frames, ignore_index=True, sort=False)