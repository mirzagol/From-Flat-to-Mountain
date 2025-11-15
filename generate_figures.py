"""Generate publication-ready figures for the cycling stage-points report."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf

DATA_PATH = Path("cycling.txt")
OUT_DIR = Path("figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Expected data file at {DATA_PATH}")
    df = pd.read_csv(
        DATA_PATH,
        sep=" ",
        skipinitialspace=True,
        engine="python",
        quotechar='"',
        names=["all_riders", "rider_class", "stage", "points", "stage_class"],
        skiprows=1,
        comment="/",
        encoding="utf-8",
    )
    stage_order = ["flat", "hills", "mount"]
    df["stage_class"] = pd.Categorical(df["stage_class"], categories=stage_order, ordered=True)
    rider_order = (
        df.groupby("rider_class")["points"].mean().sort_values(ascending=False).index.tolist()
    )
    df["rider_class"] = pd.Categorical(df["rider_class"], categories=rider_order, ordered=True)
    return df


def save_fig(fig: plt.Figure, filename: str) -> None:
    fig.savefig(OUT_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def figure_dataset_overview(df: pd.DataFrame) -> None:
    rider_counts = (
        df["rider_class"].value_counts(dropna=False).rename_axis("rider_class").reset_index(name="stage_entries")
    )
    points_by_stage = (
        df.groupby("stage_class")["points"].sum().rename("sum_points").reset_index()
    )

    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    sns.barplot(data=rider_counts, x="stage_entries", y="rider_class", palette="Blues", ax=ax)
    ax.set_xlabel("Number of Stage Entries")
    ax.set_ylabel("Rider Class")
    fig.tight_layout()
    save_fig(fig, "fig_dataset_entries.png")

    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    sns.barplot(data=points_by_stage, x="stage_class", y="sum_points", palette="viridis", ax=ax)
    ax.set_xlabel("Stage Profile")
    ax.set_ylabel("Total Points")
    fig.tight_layout()
    save_fig(fig, "fig_dataset_stage_points.png")


def figure_top_riders(df: pd.DataFrame) -> None:
    top_riders = (
        df.groupby("all_riders", as_index=False)["points"].sum().sort_values("points", ascending=False).head(10)
    )
    stage_class_mix = df.groupby(["stage_class", "rider_class"], as_index=False)["points"].sum()
    stage_class_pivot = (
        stage_class_mix.pivot(index="stage_class", columns="rider_class", values="points").fillna(0)
    )

    fig, ax = plt.subplots(figsize=(6.4, 6))
    top_sorted = top_riders.sort_values("points")
    ax.barh(top_sorted["all_riders"], top_sorted["points"], color="#1f77b4")
    ax.set_xlabel("Points")
    ax.set_ylabel("Rider")
    fig.tight_layout()
    save_fig(fig, "fig_top_riders.png")

    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    stage_class_pivot.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
    ax.set_xlabel("Stage Profile")
    ax.set_ylabel("Points")
    ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left", title="Rider Class")
    fig.tight_layout()
    save_fig(fig, "fig_stage_class_mix.png")


def figure_distributions(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 5))
    sns.histplot(
        data=df,
        x="points",
        hue="rider_class",
        element="step",
        stat="density",
        common_norm=False,
        bins=40,
        ax=ax,
    )
    ax.set_xlabel("Points")
    ax.set_ylabel("Density")
    ax.set_xlim(-5, df["points"].max() * 1.05)
    fig.tight_layout()
    save_fig(fig, "fig_points_density.png")

    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    sns.boxplot(
        data=df,
        x="stage_class",
        y="points",
        hue="rider_class",
        showfliers=False,
        ax=ax,
    )
    ax.set_xlabel("Stage Profile")
    ax.set_ylabel("Points")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", title="Rider Class")
    fig.tight_layout()
    save_fig(fig, "fig_stage_boxplots.png")


def figure_interactions(df: pd.DataFrame) -> None:
    interaction_means = (
        df.groupby(["stage_class", "rider_class"], observed=True)["points"].mean().reset_index()
    )
    rider_order = df["rider_class"].cat.categories.tolist()
    stage_order = df["stage_class"].cat.categories.tolist()

    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.2])

    ax0 = fig.add_subplot(gs[0, :])
    sns.pointplot(
        data=interaction_means,
        x="stage_class",
        y="points",
        hue="rider_class",
        dodge=0.2,
        markers="o",
        linestyles="-",
        errorbar=("ci", 95),
        ax=ax0,
    )
    ax0.set_xlabel("Stage Class")
    ax0.set_ylabel("Mean Points")
    ax0.legend(title="Rider Class", bbox_to_anchor=(1.02, 1), loc="upper left")

    for idx, stage in enumerate(stage_order):
        ax = fig.add_subplot(gs[1, idx])
        subset = df[df["stage_class"] == stage]
        sns.boxplot(
            data=subset,
            x="rider_class",
            y="points",
            order=rider_order,
            showfliers=False,
            ax=ax,
        )
        ax.set_xlabel("Rider Class")
        if idx == 0:
            ax.set_ylabel("Points")
        else:
            ax.set_ylabel("")
        for label in ax.get_xticklabels():
            label.set_rotation(45)

    fig.tight_layout()
    save_fig(fig, "fig_interactions.png")


def figure_diagnostics(df: pd.DataFrame) -> None:
    model = smf.ols("points ~ C(rider_class) * C(stage_class)", data=df).fit()
    residuals = model.resid
    fitted = model.fittedvalues

    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    sm.ProbPlot(residuals).qqplot(line="s", ax=ax)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_fig(fig, "fig_residual_qq.png")

    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    ax.scatter(fitted, residuals, alpha=0.35, s=15, color="#1f77b4")
    ax.axhline(0, color="red", linestyle="--", linewidth=1)
    ax.set_xlabel("Fitted Values")
    ax.set_ylabel("Residuals")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_fig(fig, "fig_residual_scatter.png")


def main() -> None:
    df = load_data()
    figure_dataset_overview(df)
    figure_top_riders(df)
    figure_distributions(df)
    figure_interactions(df)
    figure_diagnostics(df)
    print("Saved figures:")
    for path in sorted(OUT_DIR.glob("fig_*.png")):
        print(f" - {path}")


if __name__ == "__main__":
    main()
