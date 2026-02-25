from src.quality import compute_quality_metrics


def test_compute_quality_metrics_basic():
    # Minimal sources dict
    sources = {
        "S1": {
            "entity_id": ["A", "A", "B"],  # duplicate A
            "email": ["a@test.de", None, "b@test.de"],  # one missing
        },
        "S2": {
            "entity_id": ["X", "Y"],
            "email": ["x@test.de", "y@test.de"],
        },
    }

    # Convert dict-of-lists to DataFrames
    import pandas as pd

    sources_df = {k: pd.DataFrame(v) for k, v in sources.items()}

    q = compute_quality_metrics(sources_df, primary_entity_id="entity_id")

    # 1 row per source
    assert set(q["source"].tolist()) == {"S1", "S2"}
    assert len(q) == 2

    # Required columns
    expected_cols = {"source", "rows", "columns", "missing_rate", "duplicate_rate"}
    assert expected_cols.issubset(set(q.columns))

    # Rates within bounds
    assert (q["missing_rate"] >= 0).all() and (q["missing_rate"] <= 1).all()
    assert (q["duplicate_rate"] >= 0).all() and (q["duplicate_rate"] <= 1).all()

    # Basic sanity: S1 has duplicates
    s1_dup = float(q.loc[q["source"] == "S1", "duplicate_rate"].iloc[0])
    assert s1_dup > 0