"""Student C: Matplotlib visualization and plain-text recommendations."""
def create_report(detail, daily, entities, output_dir):
    """TODO: create directory, three charts and 04_report.txt per file 12.
    Use a loop to save/annotate figures, and a condition for a management message.
    Return a list of four pathlib.Path objects. Save before closing each figure.
    """
    raise NotImplementedError('Student C: implement create_report')

"""Student C: charts and management report for solar self-consumption."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # save files without opening a window
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

RATE = "weighted_self_consumption_pct"


def fmt_date(ts):
    """Format a Timestamp like 'July 21'."""
    return f"{ts.strftime('%B')} {ts.day}"


def chart_trend(daily, path):
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(daily["date"], daily[RATE], marker="o", markersize=3, linewidth=1.5)
    overall = 100 * daily["rate_numerator"].sum() / daily["rate_denominator"].sum()
    ax.axhline(overall, linestyle="--", color="gray", linewidth=1,
               label=f"Overall weighted rate: {overall:.1f}%")

    # Annotation loop: label the lowest and highest day.
    marks = [("Lowest", daily.loc[daily[RATE].idxmin()]),
             ("Highest", daily.loc[daily[RATE].idxmax()])]
    for label, row in marks:
        ax.annotate(f"{label}: {row[RATE]:.1f}%\n{fmt_date(row['date'])}",
                    xy=(row["date"], row[RATE]),
                    xytext=(0, 22 if label == "Highest" else -34),
                    textcoords="offset points", ha="center", fontsize=9,
                    arrowprops={"arrowstyle": "->"})

    ax.set_ylim(daily[RATE].min() - 9, daily[RATE].max() + 7)
    ax.set_title("Daily Weighted Self-Consumption Rate (all buildings), Jul 1 - Aug 29, 2026")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weighted self-consumption (% of generation)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    fig.autofmt_xdate()
    ax.grid(alpha=0.3)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def chart_comparison(entities, path):
    ordered = entities.sort_values(RATE, ascending=True)  # best bar on top
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(ordered["entity_id"], ordered[RATE], color="steelblue")
    for bar, value in zip(bars, ordered[RATE]):
        ax.text(value + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{value:.1f}%", va="center", fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_title("Weighted Self-Consumption Rate by Building, Jul 1 - Aug 29, 2026")
    ax.set_xlabel("Weighted self-consumption (% of generation)")
    ax.set_ylabel("Building (entity ID)")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def chart_relationship(detail, path):
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(detail["rate_denominator"], detail["rate_numerator"], s=14, alpha=0.5)
    top = max(detail["rate_denominator"].max(), detail["rate_numerator"].max())
    ax.plot([0, top], [0, top], linestyle="--", color="gray",
            label="100% self-consumption (no export)")
    ax.set_title("Self-Consumed Energy vs Generation, per building-day")
    ax.set_xlabel("Generation (kWh per building-day)")
    ax.set_ylabel("Self-consumed energy = generation - export (kWh)")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def coverage(detail):
    """Return (observed, expected, missing key list) from the data itself."""
    dates = pd.date_range(detail["date"].min(), detail["date"].max())
    entities = sorted(detail["entity_id"].unique())
    expected = pd.MultiIndex.from_product([dates, entities])
    observed = pd.MultiIndex.from_frame(detail[["date", "entity_id"]])
    missing = expected.difference(observed)
    return len(observed), len(expected), list(missing)


def management_message(overall, spread):
    """Condition that selects the headline message."""
    if overall >= 90:
        return "Solar use is very high; little room to improve."
    if overall >= 80:
        return ("Most solar output is used locally, but the gap between best and "
                f"worst buildings ({spread:.1f} points) is worth a closer look.")
    return "A large share of solar output is exported; local use needs attention."


def build_report(detail, daily, entities):
    observed, expected, missing = coverage(detail)
    missing_txt = ", ".join(f"{e} / {fmt_date(d)}" for d, e in missing) or "none"

    overall = 100 * detail["rate_numerator"].sum() / detail["rate_denominator"].sum()
    best = entities.loc[entities[RATE].idxmax()]
    worst = entities.loc[entities[RATE].idxmin()]
    spread = best[RATE] - worst[RATE]
    low_day = daily.loc[daily[RATE].idxmin()]
    high_day = daily.loc[daily[RATE].idxmax()]

    # Grid dependence = import / load (daily netted meters, so a proxy only).
    entities = entities.assign(grid_pct=100 * entities["import_kwh"] / entities["load_kwh"])
    daily = daily.assign(grid_pct=100 * daily["import_kwh"] / daily["load_kwh"])
    grid_all = 100 * entities["import_kwh"].sum() / entities["load_kwh"].sum()
    grid_top = entities.loc[entities["grid_pct"].idxmax()]
    grid_day = daily.loc[daily["grid_pct"].idxmax()]

    # July 21 / E01 documented low-generation day: report only, no causal claim.
    case = detail[(detail["entity_id"] == "E01") & (detail["date"] == pd.Timestamp("2026-07-21"))]
    if len(case):
        c = case.iloc[0]
        case_txt = (f"E01 on July 21 had generation of {c['generation_kwh']:.0f} kWh "
                    f"and a row rate of {c['self_consumption_pct']:.1f}%. It is a "
                    "documented low-generation day and is retained. We do not "
                    "attribute any change in the daily total to it.")
    else:
        case_txt = "E01 on July 21 is not present in the data."

    zero = detail[detail["rate_denominator"] == 0]
    zero_txt = "; ".join(f"{r.entity_id} on {fmt_date(r.date)}" for r in zero.itertuples())

    lines = [
        "SOLAR ENERGY SELF-CONSUMPTION - MANAGEMENT REPORT (synthetic teaching data)",
        "=" * 72,
        "",
        f"Period: {fmt_date(detail['date'].min())} - {fmt_date(detail['date'].max())}, "
        f"{detail['date'].min().year}. Buildings: {detail['entity_id'].nunique()}.",
        f"Coverage: {observed} of {expected} expected building-days ({observed}/{expected}). "
        f"Missing key: {missing_txt} (conflicting records were quarantined).",
        f"Headline: {management_message(overall, spread)}",
        "",
        "THREE FINDINGS (calculated from the supplied tables)",
        f"1. Overall weighted self-consumption is {overall:.2f}% of generation. Buildings "
        f"range from {worst[RATE]:.2f}% ({worst['entity_id']}) to {best[RATE]:.2f}% "
        f"({best['entity_id']}), a spread of {spread:.2f} points.",
        f"2. The daily weighted rate is lowest on {fmt_date(low_day['date'])} "
        f"({low_day[RATE]:.2f}%) and highest on {fmt_date(high_day['date'])} "
        f"({high_day[RATE]:.2f}%).",
        f"3. Grid dependence (import / load) is {grid_all:.1f}% overall. It is highest "
        f"for {grid_top['entity_id']} at {grid_top['grid_pct']:.1f}% and on "
        f"{fmt_date(grid_day['date'])} at {grid_day['grid_pct']:.1f}% across all buildings.",
        "",
        "THREE FEASIBLE ACTIONS",
        f"1. Review {worst['entity_id']} (lowest rate) and compare its export pattern "
        f"with {best['entity_id']} (highest) to see what differs in daytime use.",
        f"2. Check what happened around {fmt_date(low_day['date'])} (lowest daily rate) "
        "using more detailed data before deciding on any change.",
        f"3. Investigate why {grid_top['entity_id']} imports the largest share of its load "
        "and whether shifting flexible loads to daylight hours is practical.",
        "",
        "DOCUMENTED CASES",
        case_txt,
        f"Zero-activity closure row retained: {zero_txt or 'none'}. Its rate is "
        "undefined (NaN), not 0%, and it adds nothing to weighted totals.",
        "",
        "IS A HIGHER RATE DESIRABLE?",
        "Generally yes here: a higher rate means more of the generated solar energy was "
        "used on site instead of exported. But the rate only describes generation. A "
        "building can be at 100% and still import a lot of grid power, so read it "
        "together with import / load.",
        "",
        "TWO LIMITATIONS",
        "1. Daily netting hides within-day imports and exports. These simplified meters "
        "cannot support tariff savings or battery sizing.",
        f"2. Data are synthetic and {observed}/{expected} coverage has one missing key. "
        "No causal claim or real-world impact can be made from these results; the "
        "weighted rate is a daily rate, not a measurement of cost or savings.",
    ]
    return "\n".join(lines) + "\n"


def create_report(detail, daily, entities, output_dir):
    """Save 3 charts and a text report; return the 4 paths."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    p1, p2, p3, p4 = (out / n for n in
                      ("01_trend.png", "02_comparison.png", "03_relationship.png", "04_report.txt"))
    chart_trend(daily, p1)
    chart_comparison(entities, p2)
    chart_relationship(detail, p3)
    p4.write_text(build_report(detail, daily, entities), encoding="utf-8")
    return [p1, p2, p3, p4]