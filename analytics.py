import pandas as pd


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-stall summary:
      - total inquiries
      - mean, median, min, max company size of inquirers
      - unique visitor count (one row per inquiry, so same as total here)
    """
    if df.empty:
        return pd.DataFrame()

    summary = (
        df.groupby(["stall_id", "hall_id", "stall_theme"])
        .agg(
            total_inquiries=("company_size", "count"),
            mean_company_size=("company_size", "mean"),
            median_company_size=("company_size", "median"),
            min_company_size=("company_size", "min"),
            max_company_size=("company_size", "max"),
        )
        .reset_index()
        .sort_values("total_inquiries", ascending=False)
    )

    summary["mean_company_size"] = summary["mean_company_size"].round(1)

    return summary


def hall_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Total inquiries and average company size per hall."""
    if df.empty:
        return pd.DataFrame()

    return (
        df.groupby("hall_id")
        .agg(
            total_inquiries=("company_size", "count"),
            mean_company_size=("company_size", "mean"),
        )
        .reset_index()
        .sort_values("total_inquiries", ascending=False)
        .assign(mean_company_size=lambda x: x["mean_company_size"].round(1))
    )


def theme_crossover(df: pd.DataFrame) -> pd.DataFrame:
    """
    How often did a visitor's theme differ from the stall's theme?
    Useful for seeing which themes attract cross-hall interest.
    """
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["is_crossover"] = df["visitor_theme"] != df["stall_theme"]

    return (
        df.groupby(["stall_theme", "visitor_theme"])
        .agg(count=("stall_id", "count"))
        .reset_index()
        .sort_values("count", ascending=False)
    )


def export(df: pd.DataFrame, path: str = "results.csv") -> None:
    """Export the raw inquiry log to CSV."""
    df.to_csv(path, index=False)
    print(f"Exported {len(df)} inquiry records to {path}")


def export_summary(df: pd.DataFrame, path: str = "summary.csv") -> None:
    """Export the per-stall summary to CSV."""
    summarize(df).to_csv(path, index=False)
    print(f"Exported stall summary to {path}")
