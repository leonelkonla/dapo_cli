from __future__ import annotations

from typing import Dict
import pandas as pd


def compute_quality_metrics(
    sources: Dict[str, pd.DataFrame],
    primary_entity_id: str,
) -> pd.DataFrame:
    rows = []

    for source_name, df in sources.items():
        total_rows = len(df)

        # Missing rate
        missing_cells = df.isna().sum().sum()
        total_cells = df.shape[0] * df.shape[1]
        missing_rate = missing_cells / total_cells if total_cells > 0 else 0

        # Duplicate rate (based on entity_id)
        entity_cols = [c for c in df.columns if c.lower() == primary_entity_id.lower()]
        if entity_cols:
            col = entity_cols[0]
            duplicate_rate = 1 - df[col].nunique() / len(df)
        else:
            duplicate_rate = 0

        rows.append(
            {
                "source": source_name,
                "rows": total_rows,
                "columns": df.shape[1],
                "missing_rate": round(missing_rate, 4),
                "duplicate_rate": round(duplicate_rate, 4),
            }
        )

    return pd.DataFrame(rows)