"""Stage 07: a full Mexico assessment combining every layer we built.

* Quantitative  : Bayesian strength rank from REAL international results (stage 06)
* Squad         : real player data + semantic squad profile (stage 05)
* Tactical      : formation-fit analysis vs the actual 4-1-4-1 (tactics module)
* Qualitative   : scouted, public-source intel + current tournament form

Writes data/processed/mexico_assessment.md and prints a summary.
"""

import pandas as pd

from wc2026.config import ARTIFACTS, PROCESSED, ensure_dirs
from wc2026.data.scouting import MEXICO, MEXICO_MEDIA, MEXICO_SOCIAL, SOURCES
from wc2026.features.interpretation import add_player_interpretation, interpret_team
from wc2026.features.tactics import formation_fit, interpret_formation
from wc2026.viz.plots import plot_team_rank

TEAM = "Mexico"


def _ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _load_live_x():
    """Pick up live X data if scripts/08_collect_x.py was run (else None)."""
    import json

    from wc2026.config import RAW
    from wc2026.data.x_collector import summarize_for_scouting

    path = RAW / "x_mexico_world_cup.json"
    if not path.exists():
        return None
    try:
        return summarize_for_scouting(json.loads(path.read_text()))
    except Exception:
        return None


def main() -> None:
    ensure_dirs()
    players = pd.read_csv(PROCESSED / "players_real_features.csv")
    squad = add_player_interpretation(players[players["team"] == TEAM].copy())

    strength = pd.read_csv(PROCESSED / "posterior_strength_real.csv")
    srow = strength[strength["team"] == TEAM].iloc[0]
    rank = int(srow["rank"])

    profile = interpret_team(TEAM, squad)
    tactics = interpret_formation(squad, actual=MEXICO["preferred_formation"])
    fit = formation_fit(squad)

    md = _render(rank, len(strength), srow, profile, tactics, fit, squad)
    out = PROCESSED / "mexico_assessment.md"
    out.write_text(md)

    plot_team_rank(strength, ARTIFACTS / "mexico_strength_rank.png", highlight=TEAM)

    # Console summary.
    print(f"=== MEXICO — World Cup 2026 assessment ===\n")
    print(f"Model strength (real results 2022-26): rank {rank}/{len(strength)} "
          f"| attack {srow['attack']:+.2f}, defence {srow['defence']:+.2f}")
    print(f"Squad (FIFA data): {profile['tier']}, {profile['style']}, "
          f"{profile['age_profile']}, {profile['depth']}")
    print(f"Best-fit shape: {tactics['best_formation']} "
          f"(XI {tactics['best_xi_rating']}); actual {MEXICO['preferred_formation']}")
    print(f"\n{tactics['actual_commentary']}")
    print(f"\nCurrent status: {MEXICO['tournament_status']}")
    print(f"\nFull report -> {out}")


def _render(rank, n, srow, profile, tactics, fit, squad) -> str:
    L = []
    L.append("# Mexico — World Cup 2026 Assessment\n")
    L.append("_Combines a Bayesian strength model fit on real international "
             "results, real squad data, formation analysis, and scouted "
             "public-source intel. Compiled 2026-06-19._\n")

    # 1. Headline
    L.append("## Bottom line\n")
    L.append(f"- **Model strength**: **{_ordinal(rank)} of {n}** "
             f"(attack {srow['attack']:+.2f}, defence {srow['defence']:+.2f}) — "
             "a mid-table side over the 2022–26 cycle.")
    L.append(f"- **Current form, though, is hot**: {MEXICO['tournament_status']}")
    L.append("- **Read**: the model's longer-window rating *understates* Mexico's "
             "present level; recent results (two World Cup clean sheets, a 5-1 over "
             "Serbia, draws with Portugal and Belgium) point to a team peaking at "
             "the right time, aided by host-nation conditions.")
    L.append(f"- **But the experts are cautious** ({MEXICO_MEDIA['overall_sentiment']}): "
             "pundits rate the defensive organisation yet doubt the cutting edge "
             "(ESPN: tipped for the \"round of 16 wall\"); title markets sit ~55-1. "
             "The upside case rests on a friendly home knockout path (Azteca, "
             "altitude) more than on raw squad quality.\n")

    # 2. Squad profile
    L.append("## Squad profile (real player data)\n")
    L.append(f"> {profile['narrative']}\n")
    L.append(f"- Tier **{profile['tier']}**, style **{profile['style']}** "
             f"(attack {profile['attack_index']} vs defence {profile['defence_index']}), "
             f"**{profile['age_profile']}**, **{profile['depth']}**.")
    key = squad.nlargest(6, "overall")[["name", "position", "role", "overall", "age"]]
    L.append("\n| Player | Pos | Role | Ovr | Age |")
    L.append("|---|---|---|---|---|")
    for _, p in key.iterrows():
        L.append(f"| {p['name']} | {p['position']} | {p['role']} | "
                 f"{p['overall']:.0f} | {p['age']} |")
    L.append("\n_Note: ratings/names above are FIFA-22 vintage, so some 2021-era "
             "names appear; the current call-ups are in 'Key players (scouted)' "
             "below. Swap in an FC24/FC25 dataset to refresh._\n")

    # 3. Tactics
    L.append("## Tactics & formation\n")
    L.append(f"Scouted setup under **{MEXICO['coach']}** (captain "
             f"{MEXICO['captain']}): **{MEXICO['preferred_formation']}**, from a "
             f"squad of {MEXICO['squad_makeup']['GK']} GK / "
             f"{MEXICO['squad_makeup']['DF']} DF / {MEXICO['squad_makeup']['MF']} MF "
             f"/ {MEXICO['squad_makeup']['FW']} FW.\n")
    L.append(f"{tactics['commentary']}\n")
    L.append(f"{tactics['actual_commentary']}\n")
    L.append("**Formation fit (best XI rating the squad can field in each shape):**\n")
    L.append("| Formation | XI rating | Wants |")
    L.append("|---|---|---|")
    for r in fit.itertuples():
        mark = " ⭐" if r.formation == tactics["best_formation"] else (
            " ◀ actual" if r.formation == MEXICO["preferred_formation"] else "")
        L.append(f"| {r.formation}{mark} | {r.xi_rating} | {r.needs} |")
    L.append("\n_4-1-4-1 and 4-2-3-1 share a coarse DF4/MF5/FW1 footprint, so they "
             "score alike here; scouted intel says Aguirre uses the 4-1-4-1 with "
             f"{MEXICO['captain']} as the lone screen._\n")
    L.append("**Why 4-1-4-1 over 4-4-2 / 4-3-3 for this squad:** Mexico is "
             "midfield-heavy (9 of 26) and light on out-and-out wingers, so a 4-3-3 "
             "would stretch the wide attack, while a flat 4-4-2 would waste central "
             "midfield depth. The 4-1-4-1 fields the strongest available core, "
             "screens the back four (the source of the two clean sheets), and lets "
             "midfield runners support a lone Jiménez/Giménez.\n")

    # 4. Form & scouted intel
    L.append("## Recent form (current rounds)\n")
    L.append("| Date | Opponent | Result | Comp |")
    L.append("|---|---|---|---|")
    for d, opp, res, comp in MEXICO["recent_results"]:
        L.append(f"| {d} | {opp} | {res} | {comp} |")
    L.append("")
    for note in MEXICO["narrative_notes"]:
        L.append(f"- {note}")
    L.append(f"\n**Scorers so far:** {', '.join(MEXICO['scorers_so_far'])}.\n")

    # 4b. Media & expert sentiment
    m = MEXICO_MEDIA
    L.append("## Media & expert sentiment (public sources)\n")
    L.append(f"**Overall: {m['overall_sentiment']}.** {m['sentiment_summary']}\n")
    for who, take in m["expert_takes"]:
        L.append(f"- **{who}** — {take}")
    L.append(f"\n**Betting markets:** {m['market_odds']}\n")
    L.append("_Note: Reddit/r/soccer fan sentiment could not be pulled in this "
             "environment (Reddit blocks crawlers and its JSON API returns an SPA "
             "shell). The above is editorial/expert sentiment from accessible "
             "outlets; wire in the authenticated Reddit API locally to add fan "
             "sentiment._\n")

    # 4b-ii. X / social & fan reaction
    sm = MEXICO_SOCIAL
    L.append("## X / social & fan reaction\n")
    L.append(f"**Net mood: {sm['net_mood']}.**\n")
    L.append("_Positive_")
    for p in sm["positive"]:
        L.append(f"- {p}")
    L.append("\n_Negative_")
    for nval in sm["negative"]:
        L.append(f"- {nval}")
    L.append(f"\n_{sm['caveat']}_\n")

    # Live X data, IF you ran scripts/08_collect_x.py (file present in data/raw/).
    live = _load_live_x()
    if live:
        L.append("### Live X sample (collected via X API)\n")
        L.append(f"Net mood **{live['net_mood']}** from {live['n']} posts "
                 f"(+{live['pos']} / -{live['neg']} / ={live['neutral']}).\n")
        for t in live["positive"][:2]:
            L.append(f"- 👍 {t}")
        for t in live["negative"][:2]:
            L.append(f"- 👎 {t}")
        L.append(f"\n_{live.get('caveat', '')}_\n")

    # 4c. Projected knockout path (Opta via SI)
    kp = m["knockout_path"]
    L.append("## Projected knockout path (Opta via SI)\n")
    L.append(f"- **Round of 32** — {kp['round32']}")
    L.append(f"- **Round of 16** — {kp['round16']}")
    L.append(f"- **Beyond** — {kp['later']}")
    L.append(f"- **Edge** — {kp['edge']}\n")

    # 5. Key players
    L.append("## Key players (scouted)\n")
    for name, desc in MEXICO["key_players"].items():
        L.append(f"- **{name}** — {desc}")
    L.append("")

    # Sources
    L.append("## Sources\n")
    for title, url in SOURCES:
        L.append(f"- [{title}]({url})")
    L.append("- Match results: martj42/international_results · Player data: "
             "FIFA 22 complete dataset")
    return "\n".join(L)


if __name__ == "__main__":
    main()
