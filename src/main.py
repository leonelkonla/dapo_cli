from __future__ import annotations

import os
from datetime import datetime

import typer
from rich import print

from .schemas import DatasetSchema, FieldSchema
from .config import GenerationConfig
from .generator import generate_clean
from .pollution import create_sources
from .etl import integrate_sources, normalize_strings, fill_nulls
from .quality import compute_quality_metrics
from .storage import save_csv_bundle, save_postgres_bundle

app = typer.Typer(help="DaPo+-like synthetic test data generator (minimal, smart wizard).")


def _run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ask(prompt: str, example: str) -> str:
    return input(f"{prompt} (Beispiel: {example})\n> ").strip()


@app.command()
def run(
    rows: int = typer.Option(1000, help="Number of base entities"),
    sources: int = typer.Option(3, help="Number of heterogeneous sources"),
    out_dir: str = typer.Option("outputs", help="Output root folder"),
    store: str = typer.Option("csv", help="csv | postgres"),
    pg_dsn: str = typer.Option("", help="Postgres DSN if store=postgres"),
    seed: int = typer.Option(42, help="Seed"),
):
    print("[bold]DaPo CLI (minimal)[/bold]")

    domain = _ask(
        "In welcher Branche / welchem Kontext bist du aktiv?",
        "E-Commerce / Banking / HR / Health / Logistik / Medien",
    )
    entity = _ask(
        "Welche Art Daten willst du generieren (Entität)?",
        "orders / transactions / applications / shipments / videos",
    )

    print("Welche Felder brauchst du? (kommagetrennt)")
    print("Beispiel: entity_id,email,city,amount,status,order_date")
    fields_raw = input("> ").strip()

    # Minimal “intelligence”: map common field names to types
    # If unknown => string
    def infer_dtype(name: str) -> str:
        n = name.lower()
        if "id" in n:
            return "id"
        if "email" in n:
            return "email"
        if "phone" in n or "tel" in n:
            return "phone"
        if "date" in n or "datum" in n or "time" in n:
            return "date"
        if "amount" in n or "price" in n or "betrag" in n or "kosten" in n:
            return "money"
        if "city" in n or "stadt" in n:
            return "city"
        if "status" in n:
            return "enum"
        if "company" in n or "firma" in n:
            return "company"
        if "title" in n or "titel" in n or "desc" in n:
            return "sentence"
        return "string"

    field_names = [f.strip() for f in fields_raw.split(",") if f.strip()]
    if not field_names:
        field_names = ["entity_id", "email", "city", "amount", "status", "date"]

    schema_fields = []
    for fn in field_names:
        dt = infer_dtype(fn)
        if dt == "id":
            schema_fields.append(FieldSchema(fn, "id", pattern=f"{entity.upper()}-{{seq:08d}}"))
        elif dt == "enum":
            schema_fields.append(FieldSchema(fn, "enum", values=["new", "ok", "error"]))
        elif dt == "money":
            schema_fields.append(FieldSchema(fn, "money", min_value=1, max_value=5000))
        else:
            schema_fields.append(FieldSchema(fn, dt))

    schema = DatasetSchema(domain=domain, entity=entity, fields=schema_fields, primary_entity_id="entity_id")
    schema.validate()

    cfg = GenerationConfig(rows=rows, n_sources=sources, seed=seed)

    # Phase 0: clean base
    clean = generate_clean(schema, cfg)

    # Phase 4-5: sources + gold standard
    srcs, gold = create_sources(schema, clean, cfg)

    # Phase 6: integrate + minimal ETL
    integrated = integrate_sources(srcs)
    integrated = normalize_strings(integrated)
    integrated = fill_nulls(integrated)

    # Quality metrics (Power BI-ready)
    quality_df = compute_quality_metrics(srcs, schema.primary_entity_id)

    run_folder = os.path.join(out_dir, _run_id())
    os.makedirs(run_folder, exist_ok=True)

    if store == "csv":
        save_csv_bundle(run_folder, srcs, integrated, gold, quality_df)
        print(f"[bold green]Done[/bold green] -> {run_folder}")
        return

    if store == "postgres":
        if not pg_dsn:
            raise typer.BadParameter("pg_dsn is required when store=postgres")
        save_postgres_bundle(pg_dsn, srcs, integrated, gold, quality_df)
        print("[bold green]Done[/bold green] -> Postgres tables created")
        return

    raise typer.BadParameter("store must be csv or postgres")


if __name__ == "__main__":
    app()