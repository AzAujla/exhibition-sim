"""
heatmap.py

Hall layout (matches the Excel/image mockup):

  The hall is a rectangle. The outer border IS the stall wall (red in image).
  Interior stalls (A/B/C/D) are inset islands (blue in image).
  Aisles are the floor showing between islands.

  Grid: 9 cols x 9 rows (cols 0-8, rows 0-8)

  Wall stalls:
    Top row    (row 0): _7 _8 _9 _10 _11 _12 _13 _14 _15
    Left col   (col 0): _6 _5 _4 _3 _2 _1  (rows 1-6 top-down)
    Right col  (col 8): _16 _17 _18 _19 _20 _21
    Bottom row (row 7): corners only (rest are entrances)

  Interior islands (2x2 each):
    _C: anchor (1,1)   _D: anchor (5,1)   [col 3-4 = central aisle]
    _A: anchor (1,4)   _B: anchor (5,4)   [row 3 = horizontal aisle]

  Entrances: 3 on bottom (cols 2,4,6), 2 on each side (rows 2,5)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
import numpy as np
import pandas as pd

GRID_COLS = 9
GRID_ROWS = 9

STALL_POSITIONS = {
    # Top wall (row 0)
    "7": (0, 0),
    "8": (1, 0),
    "9": (2, 0),
    "10": (3, 0),
    "11": (4, 0),
    "12": (5, 0),
    "13": (6, 0),
    "14": (7, 0),
    "15": (8, 0),
    # Left wall (col 0, rows 1-6)
    "6": (0, 1),
    "5": (0, 2),
    "4": (0, 3),
    "3": (0, 4),
    "2": (0, 5),
    "1": (0, 6),
    # Right wall (col 8, rows 1-6)
    "16": (8, 1),
    "17": (8, 2),
    "18": (8, 3),
    "19": (8, 4),
    "20": (8, 5),
    "21": (8, 6),
}

ISLAND_POSITIONS = {
    "C": (1.5, 1.5),
    "D": (5.5, 1.5),
    "A": (1.5, 4.5),
    "B": (5.5, 4.5),
}
ISLAND_SIZE = 2

# Bottom entrances (col) and side entrances (row)
BOTTOM_ENTRANCES = (2, 4, 6)
SIDE_ENTRANCES = (2, 5)

HALLS_ORDER = ["H1", "H2", "H3", "H4", "H5", "H6", "H7"]
FIGURE_COLS = 4

WALL_COLOR = "#c0392b"
FLOOR_COLOR = "#a9c4d4"
MISC_DOT = "#f39c12"
TEXT_DARK = "#1a1a1a"
TEXT_LIGHT = "#ffffff"

WALL_CMAP = LinearSegmentedColormap.from_list("wc", ["#f5b7b1", "#e74c3c", "#7b241c"])
ISLE_CMAP = LinearSegmentedColormap.from_list("ic", ["#d6eaf8", "#2980b9", "#1a5276"])


def _suffix(sid):
    return sid.split("_", 1)[1]


def _build_counts(df):
    if df.empty:
        return {}
    return df.groupby("stall_id").size().to_dict()


def _tc(rgba):
    r, g, b, _ = rgba
    return TEXT_DARK if (0.299 * r + 0.587 * g + 0.114 * b) > 0.45 else TEXT_LIGHT


def _draw_hall(ax, hall_id, counts, wnorm, inorm):
    import map_data

    hall = map_data.HALLS[hall_id]
    smap = {_suffix(s.id): s for s in hall.stalls}
    W, H = GRID_COLS, GRID_ROWS

    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    # Red wall background
    ax.add_patch(
        mpatches.Rectangle(
            (0, 0),
            W,
            H,
            facecolor=WALL_COLOR,
            edgecolor="#7b241c",
            linewidth=1.5,
            zorder=0,
        )
    )

    # Blue interior floor (cols 1-7, rows 1-7)
    ax.add_patch(
        mpatches.Rectangle(
            (1, 1), 7, 7, facecolor=FLOOR_COLOR, edgecolor="none", zorder=1
        )
    )

    # Bottom entrance cutouts
    for c in BOTTOM_ENTRANCES:
        ax.add_patch(
            mpatches.Rectangle(
                (c, H - 1), 1, 1, facecolor=FLOOR_COLOR, edgecolor="none", zorder=1
            )
        )

    # Side entrance cutouts
    for r in SIDE_ENTRANCES:
        ax.add_patch(
            mpatches.Rectangle(
                (0, r), 1, 1, facecolor=FLOOR_COLOR, edgecolor="none", zorder=1
            )
        )
        ax.add_patch(
            mpatches.Rectangle(
                (W - 1, r), 1, 1, facecolor=FLOOR_COLOR, edgecolor="none", zorder=1
            )
        )

    pad = 0.06

    # Wall stalls
    for sfx, (gc, gr) in STALL_POSITIONS.items():
        stall = smap.get(sfx)
        if not stall:
            continue
        n = counts.get(stall.id, 0)
        color = WALL_CMAP(wnorm(n))
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (gc + pad, gr + pad),
                1 - 2 * pad,
                1 - 2 * pad,
                boxstyle="round,pad=0.03",
                facecolor=color,
                edgecolor="#7b241c",
                linewidth=0.5,
                zorder=2,
            )
        )
        tc = _tc(color)
        cx, cy = gc + 0.5, gr + 0.5
        ax.text(
            cx,
            cy - 0.13,
            f"_{sfx}",
            ha="center",
            va="center",
            fontsize=3.8,
            color=tc,
            alpha=0.8,
            zorder=3,
        )
        ax.text(
            cx,
            cy + 0.16,
            str(n),
            ha="center",
            va="center",
            fontsize=5,
            fontweight="bold",
            color=tc,
            zorder=3,
        )
        if stall.misc:
            ax.plot(
                gc + 0.82,
                gr + 0.18,
                "o",
                color=MISC_DOT,
                markersize=2.8,
                markeredgecolor="white",
                markeredgewidth=0.4,
                zorder=4,
            )

    # Island stalls
    s = ISLAND_SIZE
    for sfx, (gc, gr) in ISLAND_POSITIONS.items():
        stall = smap.get(sfx)
        if not stall:
            continue
        n = counts.get(stall.id, 0)
        color = ISLE_CMAP(inorm(n))
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (gc + pad, gr + pad),
                s - 2 * pad,
                s - 2 * pad,
                boxstyle="round,pad=0.05",
                facecolor=color,
                edgecolor="#1a5276",
                linewidth=0.8,
                zorder=2,
            )
        )
        tc = _tc(color)
        cx, cy = gc + s / 2, gr + s / 2
        ax.text(
            cx,
            cy - 0.2,
            f"_{sfx}",
            ha="center",
            va="center",
            fontsize=5.5,
            color=tc,
            alpha=0.8,
            zorder=3,
        )
        ax.text(
            cx,
            cy + 0.25,
            str(n),
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color=tc,
            zorder=3,
        )
        if stall.misc:
            ax.plot(
                gc + s - 0.2,
                gr + 0.2,
                "o",
                color=MISC_DOT,
                markersize=3.5,
                markeredgecolor="white",
                markeredgewidth=0.5,
                zorder=4,
            )

    ax.set_title(
        f"{hall_id}  ·  {hall.theme}",
        fontsize=8,
        fontweight="bold",
        color="#2c3e50",
        pad=4,
    )


def _render(df):
    counts = _build_counts(df)
    maxc = max(counts.values(), default=1)
    wnorm = Normalize(0, maxc)
    inorm = Normalize(0, maxc)

    fc = FIGURE_COLS
    fr = int(np.ceil(len(HALLS_ORDER) / fc))
    cpx, pad = 0.56, 0.7

    fig, axes = plt.subplots(
        fr,
        fc,
        figsize=(
            fc * (GRID_COLS * cpx + pad) + 2.0,
            fr * (GRID_ROWS * cpx + pad) + 1.2,
        ),
        facecolor="#e8edf2",
    )
    axes_flat = np.array(axes).flatten()

    for i, hid in enumerate(HALLS_ORDER):
        _draw_hall(axes_flat[i], hid, counts, wnorm, inorm)
    for j in range(len(HALLS_ORDER), len(axes_flat)):
        axes_flat[j].set_facecolor("#e8edf2")
        axes_flat[j].axis("off")

    fig.subplots_adjust(right=0.87)

    sm_w = ScalarMappable(cmap=WALL_CMAP, norm=wnorm)
    sm_w.set_array([])
    sm_i = ScalarMappable(cmap=ISLE_CMAP, norm=inorm)
    sm_i.set_array([])

    cax1 = fig.add_axes([0.905, 0.55, 0.015, 0.35])
    cax2 = fig.add_axes([0.905, 0.12, 0.015, 0.35])

    cb1 = fig.colorbar(sm_w, cax=cax1)
    cb1.set_label("Wall stall\ninquiries", fontsize=7.5, color="#555")
    cb1.ax.tick_params(labelsize=7, colors="#555")
    cb1.outline.set_edgecolor("#aaa")

    cb2 = fig.colorbar(sm_i, cax=cax2)
    cb2.set_label("Interior stall\ninquiries", fontsize=7.5, color="#555")
    cb2.ax.tick_params(labelsize=7, colors="#555")
    cb2.outline.set_edgecolor("#aaa")

    misc_h = plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor=MISC_DOT,
        markersize=7,
        label="Misc / wildcard stall",
    )
    fig.legend(
        handles=[misc_h],
        loc="lower right",
        fontsize=8,
        framealpha=0.9,
        edgecolor="#ccc",
        bbox_to_anchor=(0.90, 0.01),
    )

    fig.suptitle(
        "Exhibition Inquiry Heatmap",
        fontsize=14,
        fontweight="bold",
        color="#1a1a2e",
        y=1.005,
    )
    fig.tight_layout(h_pad=1.2, w_pad=1.0, rect=[0, 0, 0.9, 1])
    return fig


def show(df):
    _render(df).show()


def save(df, path="heatmap.png", dpi=200):
    fig = _render(df)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved heatmap to {path}")
