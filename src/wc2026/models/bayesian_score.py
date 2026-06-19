"""Hierarchical Bayesian Poisson model of match scorelines (PyMC).

The model
=========
For a match between home team ``h`` and away team ``a`` we treat the goals each
side scores as Poisson counts whose (log) rates depend on an attack and a
defence ability per team::

    home_goals ~ Poisson(λ_home)
    away_goals ~ Poisson(λ_away)

    log λ_home = intercept + home_adv + att[h] - def[a]
    log λ_away = intercept            + att[a] - def[h]

Why hierarchical / "partial pooling"?
-------------------------------------
Each team's att/def is drawn from a shared distribution whose spread (σ) is
itself estimated. Teams with few matches are pulled toward the league average;
teams with many matches keep their own signal. This is the Bayesian cure for
small samples -- far more robust than fitting 48 independent strengths.

Where your player analytics enter
----------------------------------
The PRIOR MEAN of each team's attack ability is set to the ``prior_strength``
covariate engineered from player skills/longevity/social reach::

    att[t] ~ Normal(beta_prior * prior_strength[t], σ_att)

So before a single goal is observed, squads with stronger players are expected
to attack better -- and the match data then updates that belief. ``beta_prior``
is itself estimated, so the model decides how much to trust your covariate.

Identifiability
---------------
Attack/defence are only defined up to a constant, so we use zero-sum
("ZeroSumNormal") parameters -- the abilities are forced to average to zero,
with the overall scoring level absorbed by ``intercept``.
"""

from __future__ import annotations

from dataclasses import dataclass

import arviz as az
import numpy as np
import pandas as pd
import pymc as pm

from ..config import SEED


@dataclass
class FitResult:
    idata: az.InferenceData
    teams: list[str]            # index order of att/def parameters
    team_to_idx: dict[str, int]


def recency_weights(dates, asof, half_life_days: float = 540.0) -> np.ndarray:
    """Exponential time-decay weights (mean-normalized to 1).

    Recent matches count more; mean-normalizing keeps the *total* likelihood
    mass the same, so this re-weights toward current form rather than just
    shrinking everything. half_life_days=540 ≈ 18 months.
    """
    age = (pd.Timestamp(asof) - pd.to_datetime(pd.Series(list(dates)))).dt.days
    age = age.clip(lower=0).to_numpy()
    w = 0.5 ** (age / half_life_days)
    return w * (len(w) / w.sum())


def build_model(
    matches: pd.DataFrame,
    teams: list[str],
    prior_strength: np.ndarray | None = None,
    weights: np.ndarray | None = None,
) -> pm.Model:
    """Construct the PyMC model. ``matches`` needs home/away team + goals.

    If ``weights`` (one per match) is given, the Poisson likelihood is
    weighted — used for recency weighting (down-weight stale matches).
    """
    team_to_idx = {t: i for i, t in enumerate(teams)}
    n_teams = len(teams)

    h_idx = matches["home_team"].map(team_to_idx).to_numpy()
    a_idx = matches["away_team"].map(team_to_idx).to_numpy()
    hg = matches["home_goals"].to_numpy()
    ag = matches["away_goals"].to_numpy()

    if prior_strength is None:
        prior_strength = np.zeros(n_teams)

    coords = {"team": teams, "match": np.arange(len(matches))}
    with pm.Model(coords=coords) as model:
        prior = pm.Data("prior_strength", prior_strength, dims="team")

        # Global scoring level and home advantage.
        intercept = pm.Normal("intercept", mu=0.0, sigma=1.0)
        home_adv = pm.Normal("home_adv", mu=0.25, sigma=0.25)

        # How strongly the player-derived covariate shifts attacking ability.
        beta_prior = pm.Normal("beta_prior", mu=0.0, sigma=1.0)

        # Hierarchical spread of abilities (partial pooling).
        sigma_att = pm.HalfNormal("sigma_att", sigma=0.5)
        sigma_def = pm.HalfNormal("sigma_def", sigma=0.5)

        # NON-CENTERED parameterization. We sample standardized zero-sum
        # offsets and scale them by sigma, rather than sampling abilities whose
        # prior width is itself a parameter. This breaks the "funnel"
        # (sigma near zero -> tiny, highly-correlated ability space) that makes
        # the centered version sample badly. The residual att offset is also
        # kept SEPARATE from the covariate term so `beta_prior` and the offsets
        # don't trade off against each other (a non-identifiable ridge).
        att_raw = pm.ZeroSumNormal("att_raw", sigma=1.0, dims="team")
        def_raw = pm.ZeroSumNormal("def_raw", sigma=1.0, dims="team")
        att = pm.Deterministic("att", sigma_att * att_raw, dims="team")
        deff = pm.Deterministic("def", sigma_def * def_raw, dims="team")

        # Effective attack = covariate nudge (player analytics) + residual.
        att_eff = pm.Deterministic("att_eff", beta_prior * prior + att, dims="team")

        log_lambda_home = intercept + home_adv + att_eff[h_idx] - deff[a_idx]
        log_lambda_away = intercept + att_eff[a_idx] - deff[h_idx]

        if weights is None:
            pm.Poisson("home_goals", mu=pm.math.exp(log_lambda_home),
                       observed=hg, dims="match")
            pm.Poisson("away_goals", mu=pm.math.exp(log_lambda_away),
                       observed=ag, dims="match")
        else:
            # Weighted likelihood: scale each match's log-prob by its recency
            # weight (via Potential, since pm.Poisson takes no per-obs weights).
            w = pm.Data("obs_weights", np.asarray(weights, float), dims="match")
            lp_h = pm.logp(pm.Poisson.dist(mu=pm.math.exp(log_lambda_home)), hg)
            lp_a = pm.logp(pm.Poisson.dist(mu=pm.math.exp(log_lambda_away)), ag)
            pm.Potential("home_goals_w", pm.math.sum(w * lp_h))
            pm.Potential("away_goals_w", pm.math.sum(w * lp_a))

    return model


def fit(
    matches: pd.DataFrame,
    teams: list[str],
    prior_strength: np.ndarray | None = None,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    target_accept: float = 0.9,
    weights: np.ndarray | None = None,
) -> FitResult:
    """Sample the posterior with NUTS and return inference data."""
    model = build_model(matches, teams, prior_strength, weights=weights)
    with model:
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            target_accept=target_accept,
            random_seed=SEED,
            progressbar=True,
        )
    return FitResult(idata=idata, teams=teams,
                     team_to_idx={t: i for i, t in enumerate(teams)})


def predict_match(idata, teams, home, away, neutral=True, max_goals=8, shifts=None):
    """Posterior-predictive GOAL forecast for one fixture.

    This is the goals-vs-winners answer made explicit. For every posterior draw
    we form each side's Poisson rate λ = exp(intercept [+ home_adv] + att - def),
    build the scoreline probability matrix, and average over draws — so the
    result carries the model's parameter uncertainty, not a point estimate.

    Returns expected goals, the most-likely scoreline, the full 1X2 split, and
    common betting-style markets (over 2.5, both-teams-to-score).
    """
    import numpy as np
    from scipy.stats import poisson

    post = idata.posterior
    i, j = teams.index(home), teams.index(away)
    flat = lambda v: post[v].to_numpy().reshape(-1, *post[v].shape[2:])
    intercept = flat("intercept")
    home_adv = flat("home_adv") if not neutral else 0.0
    att = flat("att_eff")          # (draws, team)
    deff = flat("def")

    # Optional momentum/sentiment nudge: a small log-rate shift to each team's
    # attack (e.g. recent form). shifts is {team_name: float}; default 0.
    sh = shifts or {}
    sh_h, sh_a = float(sh.get(home, 0.0)), float(sh.get(away, 0.0))

    lam_h = np.exp(intercept + home_adv + att[:, i] + sh_h - deff[:, j])
    lam_a = np.exp(intercept + att[:, j] + sh_a - deff[:, i])

    g = np.arange(max_goals + 1)
    # Joint scoreline matrix: average the per-draw outer products (shared λ per
    # draw induces realistic correlation between the two scores).
    M = np.zeros((max_goals + 1, max_goals + 1))
    ph = np.stack([poisson.pmf(x, lam_h) for x in g])   # (goals, draws)
    pa = np.stack([poisson.pmf(y, lam_a) for y in g])
    for x in g:
        for y in g:
            M[x, y] = np.mean(ph[x] * pa[y])
    M /= M.sum()

    hx, ax = np.unravel_index(M.argmax(), M.shape)
    return {
        "home": home, "away": away, "neutral": neutral,
        "exp_goals_home": round(float(lam_h.mean()), 2),
        "exp_goals_away": round(float(lam_a.mean()), 2),
        "most_likely_score": f"{hx}-{ax}",
        "p_home_win": round(float(np.tril(M, -1).sum()), 3),
        "p_draw": round(float(np.trace(M)), 3),
        "p_away_win": round(float(np.triu(M, 1).sum()), 3),
        "p_over_2_5": round(float(sum(M[x, y] for x in g for y in g if x + y >= 3)), 3),
        "p_btts": round(float(sum(M[x, y] for x in g[1:] for y in g[1:])), 3),
        "score_matrix": M,
    }


def posterior_strength_table(fit_result: FitResult) -> pd.DataFrame:
    """Posterior mean attack/defence per team, sorted by net strength."""
    post = fit_result.idata.posterior
    att = post["att_eff"].mean(dim=("chain", "draw")).to_numpy()
    deff = post["def"].mean(dim=("chain", "draw")).to_numpy()
    df = pd.DataFrame({
        "team": fit_result.teams,
        "attack": att,
        "defence": deff,
        "net_strength": att + deff,
    }).sort_values("net_strength", ascending=False).reset_index(drop=True)
    return df
