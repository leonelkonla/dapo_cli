from src.schemas import DatasetSchema, FieldSchema
from src.config import GenerationConfig
from src.generator import generate_clean


def test_generate_clean_smoke():
    schema = DatasetSchema(
        domain="test",
        entity="customers",
        fields=[
            FieldSchema("entity_id", "id", pattern="CUST-{seq:05d}"),
            FieldSchema("email", "email"),
            FieldSchema("city", "city"),
        ],
    )
    cfg = GenerationConfig(rows=50, seed=1)

    df = generate_clean(schema, cfg)
    assert len(df) == 50
    assert "entity_id" in df.columns
    assert "email" in df.columns