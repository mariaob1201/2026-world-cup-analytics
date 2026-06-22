# Simulation-Based Inference (SBI) — where it fits

**Short version:** the project's core model has a *tractable* likelihood
(Poisson / Gamma), so exact Bayesian **MCMC is preferred** — SBI would trade
exactness for nothing. SBI earns its place only when the simulator becomes rich
enough that the likelihood can't be written down.

## The demo (`make sbi-demo`)

A rejection-ABC ([models/abc.py](../src/wc2026/models/abc.py)) infers **home
advantage** and **two team strengths** from the simulator alone — no likelihood,
just simulate-and-match on five summary statistics — and is compared to the
ground truth and to exact MCMC:

| parameter | truth | ABC (likelihood-free) | exact MCMC |
|---|---|---|---|
| home_adv | 0.30 | 0.30 | 0.35 |
| str(T0, strong) | 0.80 | 0.71 | 0.76 |
| str(T5, weak) | −0.80 | −0.77 | −0.78 |

**ABC ≈ MCMC ≈ truth** — the likelihood-free method works here and agrees with
exact inference. (Numbers are seed-dependent; regenerate with `make sbi-demo`.)

## When you'd actually switch to SBI

The moment you make the **match simulator** realistic in ways that break the
closed-form likelihood — game-state dependence (teams sit deeper when ahead),
fatigue across the tournament, red cards, possession chains, spatial build-up —
there's no `pm.Poisson(...)` to write, but you can still *simulate* a match. Then:

```
team/style params → match simulator → simulated summary stats
                          ▲                    │
                          └── infer params so simulated ≈ observed stats
                              (ABC, or neural SBI: the `sbi` package, SNPE/SNRE)
```

You already have both halves: a **simulator** (the tournament Monte Carlo) and the
**summary statistics** (goals, shots, SoT, xG, possession, territory, press). The
missing piece is a mechanistic match simulator; `models/abc.py` is the scaffold it
would plug into.

## Honest tradeoffs

- SBI is heavier (thousands–millions of simulations) and sensitive to
  **summary-statistic choice** (drop information → biased posterior).
- Validate the SBI posterior with **SBC** (simulation-based calibration) and the
  usual **RPS scoreboard** — it only earns its place if it predicts better.
- Don't adopt it for the current model: tractable likelihood ⇒ exact MCMC wins.
