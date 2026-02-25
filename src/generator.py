from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from faker import Faker

from .schemas import DatasetSchema, FieldSchema
from .config import GenerationConfig


def _rand_date(fake: Faker, start_days: int, end_days: int) -> str:
    start = datetime.utcnow() + timedelta(days=start_days)
    end = datetime.utcnow() + timedelta(days=end_days)
    dt = fake.date_between(start_date=start.date(), end_date=end.date())
    return dt.isoformat()


def _gen_value(fake: Faker, rnd: random.Random, field: FieldSchema, seq: int) -> Any:
    t = field.dtype.lower()

    if t == "id":
        pattern = field.pattern or "ID-{seq:08d}"
        return pattern.format(seq=seq)

    if t == "string":
        return fake.word()

    if t == "text":
        return fake.text(max_nb_chars=80)

    if t == "sentence":
        return fake.sentence(nb_words=6)

    if t == "email":
        return fake.email()

    if t == "phone":
        return fake.phone_number()

    if t == "city":
        return fake.city()

    if t == "company":
        return fake.company()

    if t == "date":
        # default: last 365 days
        return _rand_date(fake, start_days=-365, end_days=0)

    if t == "int":
        mn = int(field.min_value) if field.min_value is not None else 0
        mx = int(field.max_value) if field.max_value is not None else 1000
        return rnd.randint(mn, mx)

    if t == "float":
        mn = float(field.min_value) if field.min_value is not None else 0.0
        mx = float(field.max_value) if field.max_value is not None else 1000.0
        return round(rnd.uniform(mn, mx), 3)

    if t in ("money",):
        mn = float(field.min_value) if field.min_value is not None else 0.0
        mx = float(field.max_value) if field.max_value is not None else 1000.0
        return round(rnd.uniform(mn, mx), 2)

    if t == "enum":
        if not field.values:
            return "unknown"
        return rnd.choice(field.values)

    # fallback
    return fake.word()


def generate_clean(schema: DatasetSchema, config: GenerationConfig) -> pd.DataFrame:
    schema.validate()

    fake = Faker(["de_DE", "en_US", "fr_FR"])
    Faker.seed(config.seed)
    rnd = random.Random(config.seed)

    rows = []
    for i in range(config.rows):
        row = {}
        for f in schema.fields:
            row[f.name] = _gen_value(fake, rnd, f, seq=i)
        rows.append(row)

    return pd.DataFrame(rows)