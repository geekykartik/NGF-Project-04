"""Student B implementation: Solar Energy Self-Consumption Analytics."""
def calculate_metrics(clean):
    """Return detail, daily, entities. TODO: copy input, add specified metrics,
    handle zero denominators, aggregate using matching sums. See file 12.
    Use a helper for safe division and a condition; do not hard-code totals.
    """
    raise NotImplementedError('Student B: implement calculate_metrics')
    
"""Student B: solar self-consumption metrics."""

import numpy as np
import pandas as pd


SOURCE_NUMERIC_COLUMNS = [
    "generation_kwh",
    "load_kwh",
    "export_kwh",
    "import_kwh",
]


def safe(a, b):
    """Divide a by b; return NaN wherever the denominator is zero."""
    if isinstance(b, pd.Series):
        return a.div(b.where(b != 0, np.nan))
    return np.nan if b == 0 else a / b


def calculate_metrics(clean):
    """Return detail, daily, and entity metric DataFrames."""
    detail = clean.copy(deep=True)

    detail["self_consumed_kwh"] = (
        detail["generation_kwh"] - detail["export_kwh"]
    )
    detail["balance_gap_kwh"] = (
        detail["generation_kwh"]
        + detail["import_kwh"]
        - detail["load_kwh"]
        - detail["export_kwh"]
    )
    detail["rate_numerator"] = (
        detail["generation_kwh"] - detail["export_kwh"]
    )
    detail["rate_denominator"] = detail["generation_kwh"]
    detail["self_consumption_pct"] = (
        100 * safe(detail["rate_numerator"], detail["rate_denominator"])
    )

    sum_columns = SOURCE_NUMERIC_COLUMNS + [
        "rate_numerator",
        "rate_denominator",
    ]

    daily = (
        detail.groupby("date", as_index=False)
        .agg({
            **{column: "sum" for column in sum_columns},
            "entity_id": "size",
        })
        .rename(columns={"entity_id": "observed_rows"})
        .sort_values("date")
        .reset_index(drop=True)
    )
    daily["weighted_self_consumption_pct"] = (
        100 * safe(daily["rate_numerator"], daily["rate_denominator"])
    )

    entities = (
        detail.groupby("entity_id", as_index=False)
        .agg({column: "sum" for column in sum_columns})
        .sort_values("entity_id")
        .reset_index(drop=True)
    )
    entities["weighted_self_consumption_pct"] = (
        100 * safe(entities["rate_numerator"], entities["rate_denominator"])
    )

    return detail, daily, entities
