"""Lightweight matplotlib helpers for inspecting the results."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless: write files, never pop a window
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def social_card(strength: pd.DataFrame, facts: dict, path,
                handle: str = "@your_handle") -> None:
    """A portrait (1080x1350) Instagram/X-ready summary card — real data only.

    ``facts`` keys: team, flag, rank, n, group_line, formation, sentiment,
    refs (list of (team, net_strength) to show as comparison bars).
    """
    bg, fg, accent, muted = "#0b1f17", "#f2fff7", "#2ecc71", "#9fb4a8"
    fig = plt.figure(figsize=(9, 11.25), dpi=120)
    fig.patch.set_facecolor(bg)
    fig.subplots_adjust(left=0.08, right=0.92, top=0.99, bottom=0.04)

    def text(x, y, s, size, color=fg, weight="normal", ha="left"):
        fig.text(x, y, s, fontsize=size, color=color, weight=weight, ha=ha)

    t = facts
    # Tricolor accent stripe (emoji flags render as tofu in matplotlib fonts).
    import matplotlib.patches as mpatches
    for i, c in enumerate(t.get("colors", ["#006847", "#ffffff", "#ce1126"])):
        fig.patches.append(mpatches.Rectangle(
            (0.08 + i * 0.045, 0.955), 0.045, 0.013, facecolor=c, edgecolor="none",
            transform=fig.transFigure, figure=fig))
    text(0.08, 0.915, t["team"].upper(), 36, fg, "bold")
    text(0.08, 0.875, "World Cup 2026 — by the numbers", 17, accent, "bold")

    # Big headline stat: model rank.
    text(0.08, 0.80, f"#{t['rank']}", 80, fg, "bold")
    text(0.34, 0.805, f"of {t['n']}", 26, muted)
    text(0.08, 0.745, "Bayesian model strength (real international results, 2022–26)",
         13, muted)

    # Fact lines.
    rows = [("Group A", t["group_line"]),
            ("Formation", t["formation"]),
            ("Fan mood", t["sentiment"])]
    y = 0.685
    for label, val in rows:
        text(0.08, y, label.upper(), 13, accent, "bold")
        text(0.08, y - 0.028, val, 16, fg)
        y -= 0.075

    # Comparison bars (net strength vs reference teams).
    ax = fig.add_axes([0.17, 0.10, 0.75, 0.29])
    ax.set_facecolor(bg)
    refs = t["refs"]
    names = [r[0] for r in refs]
    vals = [r[1] for r in refs]
    colors = [accent if n == t["team"] else "#35506f" for n in names]
    ax.barh(names[::-1], vals[::-1], color=colors[::-1])
    ax.set_title("Net strength vs the field", color=fg, loc="left", fontsize=14)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=fg, labelsize=12)
    ax.set_xticks([])

    text(0.08, 0.055, f"Bayesian Poisson model · {handle}", 12, muted)
    text(0.08, 0.030,
         "Data: FIFA player ratings · martj42 results · ESPN/SI. Illustrative, not betting advice.",
         9, muted)
    fig.savefig(path, facecolor=bg)
    plt.close(fig)


def plot_champion_probs(sim: pd.DataFrame, path, top: int = 15) -> None:
    """Horizontal bar chart of the top-N title probabilities."""
    d = sim.nlargest(top, "p_champion").iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.4 * top + 1))
    ax.barh(d["team"], 100 * d["p_champion"], color="#2b8cbe")
    ax.set_xlabel("P(win World Cup 2026)  [%]")
    ax.set_title("Bayesian title probabilities")
    for y, v in enumerate(d["p_champion"]):
        ax.text(100 * v + 0.2, y, f"{100 * v:.1f}%", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_team_rank(strength: pd.DataFrame, path, highlight: str) -> None:
    """All 48 teams by net strength, with one team highlighted."""
    d = strength.sort_values("net_strength", ascending=False).reset_index(drop=True)
    colors = ["#d94801" if t == highlight else "#9ecae1" for t in d["team"]]
    fig, ax = plt.subplots(figsize=(8, 11))
    ax.barh(d["team"][::-1], d["net_strength"][::-1], color=colors[::-1])
    rank = int(d.index[d["team"] == highlight][0]) + 1
    ax.set_xlabel("posterior net strength (attack + defence)")
    ax.set_title(f"WC2026 team strength from real results — {highlight} = {rank}/48")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_strength(strength: pd.DataFrame, path, top: int = 20) -> None:
    """Posterior attack vs defence scatter for the strongest teams."""
    d = strength.nlargest(top, "net_strength")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(d["attack"], d["defence"], color="#cb181d")
    for _, r in d.iterrows():
        ax.annotate(r["team"], (r["attack"], r["defence"]), fontsize=8,
                    xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("attack (higher = scores more)")
    ax.set_ylabel("defence (higher = concedes less)")
    ax.set_title("Posterior mean team strengths")
    ax.axhline(0, color="grey", lw=0.5)
    ax.axvline(0, color="grey", lw=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
