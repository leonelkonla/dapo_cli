from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FieldSchema:
    name: str
    dtype: str  # string, int, float, money, date, email, phone, city, enum, id, text, sentence, company
    nullable: bool = False

    # optional constraints / params
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    values: Optional[List[str]] = None      # for enum
    pattern: Optional[str] = None           # for id patterns like "ORD-{seq:08d}"


@dataclass
class DatasetSchema:
    domain: str
    entity: str
    fields: List[FieldSchema] = field(default_factory=list)
    primary_entity_id: str = "entity_id"

    def validate(self) -> None:
        if not self.fields:
            raise ValueError("Schema must contain at least one field.")

        names = [f.name for f in self.fields]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate field names detected.")

        if not any(f.name == self.primary_entity_id for f in self.fields):
            # auto-insert entity_id if missing
            self.fields.insert(
                0,
                FieldSchema(
                    name=self.primary_entity_id,
                    dtype="id",
                    pattern=f"{self.entity.upper()}-{{seq:08d}}",
                    nullable=False,
                ),
            )