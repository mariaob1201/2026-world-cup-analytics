"""Rejection Approximate Bayesian Computation (a Simulation-Based Inference method).

Likelihood-free inference: given only a *simulator* and *summary statistics*, infer
parameters by simulating from the prior and keeping the draws whose simulated
summaries land closest to the observed ones. Used here as a methods demo (the
project's main model has a tractable likelihood, so exact MCMC is preferred) — and
as the scaffold for fitting a richer match simulator whose likelihood can't be
written. See ``scripts/26_sbi_abc.py``.
"""

from __future__ import annotations

import numpy as np

TEAMS = ["T0", "T1", "T2", "T3", "T4", "T5"]
TRUE_STR = np.array([0.8, 0.4, 0.1, -0.1, -0.4, -0.8])
TRUE_INTERCEPT = 0.15
TRUE_HOME_ADV = 0.30
TARGETS = (0, 5)


def fixtures(n_matches: int, rng):
    pairs = [rng.choice(len(TEAMS), 2, replace=False) for _ in range(n_matches)]
    return np.array([p[0] for p in pairs]), np.array([p[1] for p in pairs])


def simulate(strength, home_adv, intercept, hi, ai, rng):
    lam_h = np.exp(intercept + home_adv + strength[hi] - strength[ai])
    lam_a = np.exp(intercept + strength[ai] - strength[hi])
    return rng.poisson(lam_h), rng.poisson(lam_a)


def summary(gh, ga, hi, ai):
    """Low-dim 'fingerprint' the ABC matches on."""
    def team_gd(idx):
        mh, ma = hi == idx, ai == idx
        d = np.concatenate([gh[mh] - ga[mh], ga[ma] - gh[ma]])
        return d.mean() if len(d) else 0.0
    return np.array([gh.mean(), ga.mean(), (gh > ga).mean(),
                     team_gd(TARGETS[0]), team_gd(TARGETS[1])])


def abc_infer(obs_summary, hi, ai, n_sims: int = 12000, keep: float = 0.02, seed: int = 1):
    """Rejection ABC over (home_adv, str[T0], str[T5]); other strengths fixed.
    Returns accepted posterior samples per parameter."""
    rng = np.random.default_rng(seed)
    draws = np.column_stack([
        rng.uniform(0.0, 0.6, n_sims),
        rng.uniform(0.0, 1.5, n_sims),
        rng.uniform(-1.5, 0.0, n_sims),
    ])
    sims = np.empty((n_sims, len(obs_summary)))
    strength = TRUE_STR.copy()
    for k in range(n_sims):
        ha, sa, sb = draws[k]
        strength[TARGETS[0]], strength[TARGETS[1]] = sa, sb
        gh, ga = simulate(strength, ha, TRUE_INTERCEPT, hi, ai, rng)
        sims[k] = summary(gh, ga, hi, ai)
    scale = sims.std(axis=0) + 1e-9
    dist = np.sqrt((((sims - obs_summary) / scale) ** 2).sum(axis=1))
    accept = draws[np.argsort(dist)[: int(n_sims * keep)]]
    return {"home_adv": accept[:, 0], "str_T0": accept[:, 1], "str_T5": accept[:, 2]}
