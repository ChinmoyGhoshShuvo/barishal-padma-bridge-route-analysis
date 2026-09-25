"""
Charts rebuilt from the report's tables (data/*.csv). Nothing is estimated.
Run:  python make_figures.py   -> PNGs in ../images/
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
DATA, OUT = HERE / "data", HERE.parent / "images"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200,
    "savefig.bbox": "tight", "figure.facecolor": "white",
})
FACTOR_COL = {"Road composition": "#0072B2", "Route coverage": "#E69F00", "Total cost": "#009E73",
              "Total time": "#CC79A7", "Total distance": "#56B4E9"}
ROUTES = ["Existing", "Shortest", "Potential"]


def weighted_scores():
    d = pd.read_csv(DATA / "route_weighted_scores.csv", comment="#").set_index("factor")
    fig, ax = plt.subplots(figsize=(6.4, 2.5))
    left = pd.Series(0.0, index=ROUTES)
    for f, col in FACTOR_COL.items():
        vals = d.loc[f, "priority"] * d.loc[f, ROUTES]
        ax.barh(ROUTES, vals, left=left, color=col, height=0.6, edgecolor="white", linewidth=0.5,
                label=f"{f} ({d.loc[f, 'priority']:.3f})")
        left += vals
    for y, r in enumerate(ROUTES):
        ax.text(left[r] + 0.01, y, f"{left[r]:.3f}", va="center", fontweight="bold", fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 0.9)
    ax.set_xlabel("Weighted score (AHP priority x route score)")
    ax.set_title("The existing route scores highest", loc="left")
    ax.legend(title="Factor (AHP weight)", title_fontsize=7, fontsize=7, frameon=False,
              loc="upper left", bbox_to_anchor=(1.01, 1.0))
    fig.text(0, -0.1, "Rebuilt from report Tables 3 and 9.", fontsize=7, color="#555")
    fig.savefig(OUT / "route-weighted-scores.png")
    plt.close(fig)


def composition():
    d = pd.read_csv(DATA / "route_road_composition.csv", comment="#")
    d["road_class"] = d.road_class.replace({"Motorway link": "Motorway", "Unclassified": "Other",
                                            "Residential": "Other"})
    p = d.groupby(["route", "road_class"]).percent.sum().unstack(fill_value=0).loc[ROUTES]
    order = ["Trunk", "Motorway", "Primary", "Secondary", "Tertiary", "Other"]
    cols = ["#D55E00", "#E69F00", "#0072B2", "#56B4E9", "#009E73", "#BBBBBB"]
    fig, ax = plt.subplots(figsize=(6.4, 2.3))
    left = pd.Series(0.0, index=ROUTES)
    for c, col in zip(order, cols):
        ax.barh(ROUTES, p[c], left=left, color=col, height=0.6, edgecolor="white", linewidth=0.5, label=c)
        for y, r in enumerate(ROUTES):
            if p.loc[r, c] >= 6:
                ax.text(left[r] + p.loc[r, c] / 2, y, f"{p.loc[r, c]:.0f}%", ha="center", va="center",
                        fontsize=7, color="white" if col in ("#D55E00", "#0072B2", "#009E73") else "black")
        left += p[c]
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of route length (%)")
    ax.set_title("Only the existing route runs mainly on trunk roads", loc="left")
    ax.legend(fontsize=7, frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    fig.text(0, -0.12, "Rebuilt from report Tables 6-8 (residential and unclassified grouped as 'Other').",
             fontsize=7, color="#555")
    fig.savefig(OUT / "route-road-class-composition.png")
    plt.close(fig)


if __name__ == "__main__":
    weighted_scores()
    composition()
    print("written to", OUT.resolve())
