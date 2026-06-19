"""Real-data adapter: build national-team squads from a public player dataset.

Source
------
The EA Sports / FIFA "complete player dataset" (sofifa-derived), hosted openly
on GitHub. ~19k real players with the exact skill schema this project uses:
``pace, shooting, passing, dribbling, defending, physic`` plus age, position,
nationality, market value and international reputation.

What this module does
----------------------
1. Download the CSV once into ``data/raw/`` (cached).
2. Map each player's ``nationality_name`` to one of our 48 World Cup teams
   (with a small alias table for naming differences).
3. Select the top ``SQUAD_SIZE`` players per nation by overall as a proxy squad.
4. Re-shape the columns to match the synthetic ``players.csv`` schema exactly,
   so ``features.player_features`` and everything downstream runs unchanged.

Honesty notes (documented proxies)
----------------------------------
* Vintage: this is FIFA 22 data, so ratings/ages predate the 2026 tournament.
  Swap ``FIFA_CSV_URL`` for a newer FC24/FC25 dump when available.
* It is a NATIONALITY POOL (top-rated players of each nation), not the official
  selected squad. Join Wikipedia's "2026 World Cup squads" by name to get the
  real call-ups.
* ``caps`` and ``debut_age`` are not in the source, so ``longevity`` is proxied
  from age and international reputation (see ``_longevity_proxies``).
* ``followers``/``social_score`` are proxied from international reputation
  (a 1-5 global-fame score) since follower APIs are paid -- see ``_social_proxy``.
"""

from __future__ import annotations

import pandas as pd

from ..config import RAW, SQUAD_SIZE
from .teams import TEAMS

FIFA_CSV_URL = (
    "https://raw.githubusercontent.com/"
    "abineshta/FIFA-22-complete-player-dataset-EDA/main/players_22.csv"
)
FIFA_CSV_LOCAL = RAW / "fifa_players_22.csv"

# Real international results (every men's international since 1872), updated live.
INTL_RESULTS_URL = (
    "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
)
INTL_RESULTS_LOCAL = RAW / "intl_results.csv"

# Our team name (martj42 convention) -> nationality string in the FIFA dataset.
FIFA_NATION_ALIASES = {
    "South Korea": "Korea Republic",
    "Czechia": "Czech Republic",
    "Türkiye": "Turkey",
    "Curaçao": "Curacao",
    "Ivory Coast": "Côte d'Ivoire",
    "Cape Verde": "Cape Verde Islands",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
}

# Our team name -> the name used in the martj42 international-results dataset.
INTL_NAME_ALIASES = {
    "Czechia": "Czech Republic",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Türkiye": "Turkey",
    "Congo DR": "DR Congo",
}

# FIFA's six skill columns -> our schema's columns.
SKILL_MAP = {
    "pace": "skill_pace",
    "shooting": "skill_shooting",
    "passing": "skill_passing",
    "dribbling": "skill_dribbling",
    "defending": "skill_defending",
    "physic": "skill_physical",
}


def download_fifa(force: bool = False) -> pd.DataFrame:
    """Load the FIFA dataset, downloading to data/raw/ on first use."""
    if FIFA_CSV_LOCAL.exists() and not force:
        return pd.read_csv(FIFA_CSV_LOCAL, low_memory=False)
    # Lazy import so the dependency is only needed when actually downloading.
    import urllib.request

    RAW.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(FIFA_CSV_URL, FIFA_CSV_LOCAL)
    return pd.read_csv(FIFA_CSV_LOCAL, low_memory=False)


def download_intl_results(force: bool = False) -> pd.DataFrame:
    """Load the international results dataset, caching to data/raw/."""
    if INTL_RESULTS_LOCAL.exists() and not force:
        return pd.read_csv(INTL_RESULTS_LOCAL, parse_dates=["date"])
    import urllib.request

    RAW.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(INTL_RESULTS_URL, INTL_RESULTS_LOCAL)
    return pd.read_csv(INTL_RESULTS_LOCAL, parse_dates=["date"])


def build_real_matches(start: str = "2022-01-01", end: str = "2026-06-19") -> pd.DataFrame:
    """Real international results in the project's matches schema.

    Filters to a recent window (so estimates reflect *current* strength, not
    decade-old form) and to our 48 teams. ``end`` defaults to "today" so we
    never train on matches that have not been played yet.
    """
    df = download_intl_results()
    df = df.dropna(subset=["home_score", "away_score"])
    df = df[(df["date"] >= start) & (df["date"] <= end)]

    # Map our canonical names to this dataset's names, filter, then map back.
    to_src = {t.name: INTL_NAME_ALIASES.get(t.name, t.name) for t in TEAMS}
    from_src = {v: k for k, v in to_src.items()}
    src_names = set(from_src)
    df = df[df["home_team"].isin(src_names) & df["away_team"].isin(src_names)].copy()
    df["home_team"] = df["home_team"].map(from_src)
    df["away_team"] = df["away_team"].map(from_src)
    df = df.sort_values("date").reset_index(drop=True)

    return pd.DataFrame({
        "match_id": range(len(df)),
        "date": df["date"].dt.date.astype(str).values,
        "home_team": df["home_team"].values,
        "away_team": df["away_team"].values,
        "home_goals": df["home_score"].astype(int).values,
        "away_goals": df["away_score"].astype(int).values,
        "tournament": df["tournament"].values,
        "neutral": df["neutral"].values,
    })


def _primary_position(player_positions: str) -> str:
    """Bucket FIFA's 'RW, ST, CF' style field into GK/DF/MF/FW."""
    primary = str(player_positions).split(",")[0].strip().upper()
    if primary == "GK":
        return "GK"
    defenders = {"CB", "LB", "RB", "LWB", "RWB"}
    mids = {"CDM", "CM", "CAM", "LM", "RM", "LCM", "RCM"}
    fwds = {"ST", "CF", "LW", "RW", "LF", "RF"}
    if primary in defenders:
        return "DF"
    if primary in mids:
        return "MF"
    if primary in fwds:
        return "FW"
    return "MF"  # safe default for anything unusual


def _longevity_proxies(age: pd.Series, reputation: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Proxy career length + caps from age and international reputation.

    No caps exist in the source, so we approximate: a pro career starts ~19,
    and more-renowned players accumulate caps faster. Clearly an estimate.
    """
    career_years = (age - 19).clip(lower=1)
    caps = (career_years * (2 + 3 * reputation)).round().clip(1, 180).astype(int)
    debut_age = (age - career_years).astype(int)
    return career_years.astype(int), caps, debut_age


def _social_proxy(reputation: pd.Series, overall: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Proxy follower count + engagement from reputation/overall.

    international_reputation (1-5) is a global-fame score; we map it to a
    plausible log-follower scale. Real follower data needs a paid API.
    """
    log_followers = 4.0 + 0.85 * reputation + 0.03 * (overall - 70)
    followers = (10 ** log_followers).round().astype("int64")
    engagement = (0.07 - 0.006 * log_followers).clip(0.002, 0.12).round(4)
    return followers, engagement


def build_real_squads(squad_size: int = SQUAD_SIZE) -> pd.DataFrame:
    """Return a players table in the project's schema, built from FIFA data."""
    fifa = download_fifa()
    code_by_team = {t.name: t.code for t in TEAMS}

    rows: list[pd.DataFrame] = []
    missing: list[str] = []
    for team in TEAMS:
        nat = FIFA_NATION_ALIASES.get(team.name, team.name)
        pool = fifa[fifa["nationality_name"] == nat]
        if pool.empty:
            missing.append(team.name)
            continue
        squad = pool.nlargest(squad_size, "overall").copy()
        squad["team"] = team.name
        squad["team_code"] = code_by_team[team.name]
        rows.append(squad)

    if missing:
        print(f"  [warn] no source players for: {', '.join(missing)} "
              f"(will get a neutral prior in the model)")

    raw = pd.concat(rows, ignore_index=True)

    # --- reshape into the canonical players.csv schema ---
    out = pd.DataFrame()
    out["player_id"] = range(len(raw))
    out["team"] = raw["team"]
    out["team_code"] = raw["team_code"]
    out["name"] = raw["short_name"]
    out["club"] = raw.get("club_name")
    out["position"] = raw["player_positions"].map(_primary_position)
    out["age"] = raw["age"].astype(int)
    out["overall"] = raw["overall"].astype(float)
    out["international_reputation"] = raw["international_reputation"].fillna(1).astype(int)

    rep = out["international_reputation"]
    cy, caps, debut = _longevity_proxies(out["age"], rep)
    out["career_years"], out["caps"], out["debut_age"] = cy, caps, debut

    # Skills: GKs have NaN for outfield skills in this source -> fill from overall.
    for fifa_col, our_col in SKILL_MAP.items():
        out[our_col] = raw[fifa_col].fillna(raw["overall"]).astype(float)

    out["market_value_eur"] = raw["value_eur"].fillna(raw["value_eur"].median()).round()
    foll, eng = _social_proxy(rep, out["overall"])
    out["followers"], out["engagement_rate"] = foll, eng

    return out
