"""The real 48 teams and 12-group draw for the 2026 FIFA World Cup.

Source: the official draw (5 Dec). Each team carries a ``latent_strength`` used
ONLY by the synthetic-demo match generator (stages 01-04); the real pipeline
(stages 05-06) fits strength from actual results and ignores it.

Name conventions here match the martj42 international-results dataset. The FIFA
player dataset uses some different spellings — see ``FIFA_NATION_ALIASES`` in
``sources.py``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Team:
    name: str
    code: str
    confederation: str
    group: str
    latent_strength: float  # illustrative; synthetic demo only


# (name, code, confederation, group, latent_strength)
_ROWS = [
    ("Mexico", "MEX", "CONCACAF", "A", 0.35),
    ("South Africa", "RSA", "CAF", "A", -0.15),
    ("South Korea", "KOR", "AFC", "A", 0.30),
    ("Czechia", "CZE", "UEFA", "A", 0.30),

    ("Canada", "CAN", "CONCACAF", "B", 0.20),
    ("Bosnia-Herzegovina", "BIH", "UEFA", "B", 0.10),
    ("Qatar", "QAT", "AFC", "B", -0.40),
    ("Switzerland", "SUI", "UEFA", "B", 0.50),

    ("Brazil", "BRA", "CONMEBOL", "C", 0.98),
    ("Morocco", "MAR", "CAF", "C", 0.55),
    ("Haiti", "HAI", "CONCACAF", "C", -0.55),
    ("Scotland", "SCO", "UEFA", "C", 0.15),

    ("United States", "USA", "CONCACAF", "D", 0.35),
    ("Paraguay", "PAR", "CONMEBOL", "D", 0.10),
    ("Australia", "AUS", "AFC", "D", 0.10),
    ("Türkiye", "TUR", "UEFA", "D", 0.40),

    ("Germany", "GER", "UEFA", "E", 0.85),
    ("Curaçao", "CUW", "CONCACAF", "E", -0.50),
    ("Ivory Coast", "CIV", "CAF", "E", 0.30),
    ("Ecuador", "ECU", "CONMEBOL", "E", 0.35),

    ("Netherlands", "NED", "UEFA", "F", 0.78),
    ("Japan", "JPN", "AFC", "F", 0.45),
    ("Sweden", "SWE", "UEFA", "F", 0.30),
    ("Tunisia", "TUN", "CAF", "F", -0.10),

    ("Belgium", "BEL", "UEFA", "G", 0.70),
    ("Egypt", "EGY", "CAF", "G", 0.15),
    ("Iran", "IRN", "AFC", "G", 0.00),
    ("New Zealand", "NZL", "OFC", "G", -0.55),

    ("Spain", "ESP", "UEFA", "H", 0.95),
    ("Cape Verde", "CPV", "CAF", "H", -0.30),
    ("Saudi Arabia", "KSA", "AFC", "H", -0.35),
    ("Uruguay", "URU", "CONMEBOL", "H", 0.60),

    ("France", "FRA", "UEFA", "I", 1.00),
    ("Senegal", "SEN", "CAF", "I", 0.45),
    ("Iraq", "IRQ", "AFC", "I", -0.35),
    ("Norway", "NOR", "UEFA", "I", 0.45),

    ("Argentina", "ARG", "CONMEBOL", "J", 1.05),
    ("Algeria", "ALG", "CAF", "J", 0.10),
    ("Austria", "AUT", "UEFA", "J", 0.35),
    ("Jordan", "JOR", "AFC", "J", -0.30),

    ("Portugal", "POR", "UEFA", "K", 0.90),
    ("Congo DR", "COD", "CAF", "K", 0.00),
    ("Uzbekistan", "UZB", "AFC", "K", -0.30),
    ("Colombia", "COL", "CONMEBOL", "K", 0.62),

    ("England", "ENG", "UEFA", "L", 0.90),
    ("Croatia", "CRO", "UEFA", "L", 0.55),
    ("Ghana", "GHA", "CAF", "L", 0.05),
    ("Panama", "PAN", "CONCACAF", "L", -0.30),
]

TEAMS: list[Team] = [Team(*r) for r in _ROWS]
GROUPS: list[str] = sorted({t.group for t in TEAMS})

# Host nations get a (designated-)home advantage in some analyses.
HOSTS = {"United States", "Mexico", "Canada"}


def team_index() -> dict[str, int]:
    return {t.name: i for i, t in enumerate(TEAMS)}


def by_group() -> dict[str, list[Team]]:
    out: dict[str, list[Team]] = {g: [] for g in GROUPS}
    for t in TEAMS:
        out[t.group].append(t)
    return out


assert len(TEAMS) == 48, "2026 World Cup has 48 teams"
assert len(GROUPS) == 12, "12 groups"
assert all(len(v) == 4 for v in by_group().values()), "4 teams per group"
