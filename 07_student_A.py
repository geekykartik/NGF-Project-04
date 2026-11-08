# """Student A implementation: project 04. See 12_dictionary.txt."""
# def load_and_clean(csv_path):
#     """Return clean, audit DataFrames. TODO: read strings; preserve source_row;
#     normalize IDs and dates; repair documented fields; validate; remove exact
#     duplicates; quarantine conflicts; sort. Use a helper, loop and mapping.
#     Keep all valid business anomalies. Never replace unknown measures with zero.
#     """
#     raise NotImplementedError('Student A: implement load_and_clean')

"""Student A: data loading, cleaning, validation and audit."""


"""Student A: data loading, cleaning, validation and audit."""

from pathlib import Path
import numpy as np
import pandas as pd


# Fixed reporting segment for each known building.
SEGMENT_BY_ENTITY = {
    "E01": "North", "E02": "North", "E03": "North", "E04": "North",
    "E05": "Central", "E06": "Central", "E07": "Central", "E08": "Central",
    "E09": "South", "E10": "South", "E11": "South", "E12": "South",
}

START_DATE = pd.Timestamp("2026-07-01")
END_DATE = pd.Timestamp("2026-08-29")

NUMERIC_COLUMNS = [
    "generation_kwh",
    "load_kwh",
    "export_kwh",
    "import_kwh",
]


def load_and_clean(csv_path):
    """Return (clean, audit) DataFrames following the project data dictionary."""

    # Read everything as text so source values are not silently reinterpreted.
    raw = pd.read_csv(csv_path, dtype=str, keep_default_na=False)

    # Physical CSV line number: header is line 1, first data row is line 2.
    data = raw.copy()
    data.insert(0, "source_row", np.arange(2, len(data) + 2))

    audit_records = []

    def log_repair(row_number, field, old_value, new_value, reason):
        audit_records.append({
            "source_row": int(row_number),
            "action": "repaired",
            "reason": (
                f"{field}: {reason} "
                f"(source={old_value!r}, normalized={new_value!r})"
            ),
        })

    # 1. Normalize entity IDs: trim whitespace and convert to uppercase.
    original_ids = data["entity_id"].copy()
    data["entity_id"] = data["entity_id"].str.strip().str.upper()

    for idx in data.index:
        if original_ids.at[idx] != data.at[idx, "entity_id"]:
            log_repair(
                data.at[idx, "source_row"], "entity_id",
                original_ids.at[idx], data.at[idx, "entity_id"],
                "trim whitespace and normalize case"
            )

    # 2. Parse ISO dates, then explicitly try DD/MM/YYYY for remaining values.
    original_dates = data["date"].copy()
    parsed_dates = pd.to_datetime(
        data["date"], format="%Y-%m-%d", errors="coerce"
    )

    alternate_format = parsed_dates.isna()
    parsed_dates.loc[alternate_format] = pd.to_datetime(
        data.loc[alternate_format, "date"],
        format="%d/%m/%Y",
        errors="coerce"
    )
    data["date"] = parsed_dates

    for idx in data.index:
        if pd.notna(data.at[idx, "date"]):
            normalized = data.at[idx, "date"].strftime("%Y-%m-%d")
            if original_dates.at[idx] != normalized:
                log_repair(
                    data.at[idx, "source_row"], "date",
                    original_dates.at[idx], normalized,
                    "parse supported date format and normalize to ISO"
                )

    # 3. Trim segment text and recover blank segments from the fixed mapping.
    original_segments = data["segment"].copy()
    data["segment"] = data["segment"].str.strip()

    for idx in data.index:
        entity = data.at[idx, "entity_id"]
        segment = data.at[idx, "segment"]

        if not segment and entity in SEGMENT_BY_ENTITY:
            data.at[idx, "segment"] = SEGMENT_BY_ENTITY[entity]
            log_repair(
                data.at[idx, "source_row"], "segment",
                original_segments.at[idx], data.at[idx, "segment"],
                "recover blank segment from fixed entity mapping"
            )
        elif original_segments.at[idx] != data.at[idx, "segment"]:
            log_repair(
                data.at[idx, "source_row"], "segment",
                original_segments.at[idx], data.at[idx, "segment"],
                "trim surrounding whitespace"
            )

    # 4. Convert numeric text. Commas are accepted as thousands separators.
    original_numeric = data[NUMERIC_COLUMNS].copy()

    for column in NUMERIC_COLUMNS:
        text_values = data[column].str.strip()
        without_commas = text_values.str.replace(",", "", regex=False)
        numeric_values = pd.to_numeric(without_commas, errors="coerce")
        data[column] = numeric_values

        for idx in data.index:
            old = original_numeric.at[idx, column]
            new = numeric_values.at[idx]

            if pd.notna(new):
                canonical = (
                    str(int(new)) if float(new).is_integer() else str(new)
                )
                if old != canonical:
                    log_repair(
                        data.at[idx, "source_row"], column, old, canonical,
                        "parse numeric text and normalize numeric formatting"
                    )

    # 5. Validate structure and values. Business anomalies are retained.
    rejection_reasons = {}

    def reject(idx, reason):
        rejection_reasons.setdefault(idx, []).append(reason)

    for idx, row in data.iterrows():
        if pd.isna(row["date"]):
            reject(idx, "invalid or impossible date")
        elif not START_DATE <= row["date"] <= END_DATE:
            reject(idx, "date outside project period")

        entity = row["entity_id"]

        if entity not in SEGMENT_BY_ENTITY:
            reject(idx, "unknown or invalid entity_id")
        elif row["segment"] != SEGMENT_BY_ENTITY[entity]:
            reject(idx, "unknown or inconsistent segment")

        for column in NUMERIC_COLUMNS:
            value = row[column]

            if pd.isna(value) or not np.isfinite(value):
                reject(idx, f"invalid numeric value in {column}")
            elif value < 0:
                reject(idx, f"negative value in {column}")

    # 6. Remove exact duplicates after normalization; keep the first.
    # source_row is excluded because each physical CSV line has a different row.
    comparison_columns = [
        column for column in data.columns if column != "source_row"
    ]
    duplicate_mask = data.duplicated(
        subset=comparison_columns, keep="first"
    )

    for idx in data.index[duplicate_mask]:
        audit_records.append({
            "source_row": int(data.at[idx, "source_row"]),
            "action": "dropped_duplicate",
            "reason": "exact duplicate after normalization; kept first occurrence",
        })

    data = data.loc[~duplicate_mask].copy()

    # 7. Quarantine invalid rows and combine their rejection reasons.
    for idx, reasons in rejection_reasons.items():
        if idx in data.index:
            audit_records.append({
                "source_row": int(data.at[idx, "source_row"]),
                "action": "quarantined",
                "reason": "; ".join(reasons),
            })

    invalid_indexes = set(rejection_reasons)
    data = data.drop(
        index=[idx for idx in invalid_indexes if idx in data.index]
    )

    # 8. If a date + entity_id key occurs more than once, quarantine every row
    # for that key. Do not average the records or choose one of them.
    conflict_mask = data.duplicated(
        subset=["date", "entity_id"], keep=False
    )
    conflict_rows = data.loc[conflict_mask]

    for _, row in conflict_rows.iterrows():
        audit_records.append({
            "source_row": int(row["source_row"]),
            "action": "quarantined",
            "reason": (
                "conflicting records share the same date and entity_id; "
                "all records for this key quarantined"
            ),
        })

    data = data.loc[~conflict_mask].copy()

    # 9. Sort the cleaned data and reset its index.
    data = data.sort_values(
        ["date", "entity_id"]
    ).reset_index(drop=True)

    clean = data.copy()

    # 10. Build the audit DataFrame.
    audit = pd.DataFrame(
        audit_records,
        columns=["source_row", "action", "reason"]
    )

    if not audit.empty:
        audit = audit.sort_values(
            ["source_row", "action", "reason"]
        ).reset_index(drop=True)

    return clean, audit
