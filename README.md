# The Substratum Theory

> *A speculative framework proposing that observable 4D reality is a dimensional projection of a 12-dimensional informational manifold.*

**Current version: v3.0 — Rigor Update (October 2026).** Every physics and mathematics statement has been brought into line with current, published science; every claim is tagged **ESTABLISHED**, **OUR HYPOTHESIS**, or **SPECULATIVE**; every displayed equation is either a standard cited result or a well-formed proposal that reduces to known physics; and every citation has been verified.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Overview

This repository contains a speculative theoretical-physics framework. It is a structured hypothesis about the architecture of reality, developed by Juan Hinojosa with assistance from Claude, an AI model by Anthropic.

**This is not established science.** It is not peer-reviewed. It is a hypothesis designed to be explored, challenged, and — where it is wrong — corrected. Version 3.0 withdrew several earlier claims that turned out to be in conflict with data or not well-formed; see the [changelog](THEORY.md#changelog).

---

## Repository Contents

| File | Description |
|------|-------------|
| `THEORY.md` | Full written framework — **v3.0**, with claim tags, verified references, open problems, changelog |
| `index.html` | Public site (GitHub Pages) presenting the v3.0 framework |
| `tools/equation_checks.py` | Python (sympy/numpy) script that checks index balance, units and numerical values of every displayed equation |
| `CONTRIBUTING.md` | How to contribute |
| `CONTRIBUTORS.md` | Credits |
| `LICENSE` | Creative Commons BY 4.0 |

---

## Core Hypothesis

### The 12-Dimensional Stack (OUR HYPOTHESIS)

| Dimensions | Function |
|------------|----------|
| 1–4 | Observable spacetime |
| 5–7 | Probability manifold (state information we experience as superposition) |
| 8–9 | Relational binding axes (correlations we experience as entanglement) |
| 10 | Observer-lock interface |
| 11–12 | Recursion and origin axes |

### What the hypothesis must reproduce (ESTABLISHED)

- 4D gravity emerges from higher-dimensional gravity only through dimensional reduction: *G₄ = G_D / Vol(Σ_n)* (Kaluza–Klein).
- The Robertson uncertainty relation σ_x σ_p ≥ ħ/2, exactly.
- Bell/CHSH: loophole-free experiments violate |S| ≤ 2; quantum mechanics never exceeds Tsirelson's 2√2; no signalling.
- Standard tunnelling probabilities and the measured in-barrier time (Ramos et al. 2020).
- Lorentz invariance to the Fermi GRB 090510 bounds, E_QG,1 > 7.6 E_Planck and E_QG,2 > 1.3 × 10¹¹ GeV (Vasileiou et al. 2013).
- Black-hole entropy, Hawking temperature, and the Page curve.

### Why 12? (ESTABLISHED context, OUR HYPOTHESIS count)

Supergravity is consistent in at most 11 dimensions; M-theory is 11-dimensional; F-theory (Vafa 1996) gives type IIB strings a 12-dimensional reading; two-time physics (Bars) derives 1-time physics as a shadow of a theory in two more dimensions. The Substratum's 12 is *motivated* by this landscape, not derived from it.

---

## Predictions (v3.0, re-examined against existing data)

1. **UHECR anisotropy** — Auger already observed a 6.5 % dipole above 8 EeV (2017). The hypothesis now requires a *distinct* signature: high-multipole power with discrete symmetry in a non-astrophysical frame, scaling as a power of energy, absent at linear order. Not detected.
2. **Entanglement saturation** — the old "> 10⁶ particles" threshold was exceeded in 2001 (10¹² atoms). Genuine multipartite entanglement now reaches 51 qubits without post-selection (2023) and a 120-qubit GHZ state with post-selection (2025). Restated: capacity must exceed 10¹² atoms in collective modes and ≳ 10² genuine parties; a finite N* is asserted but not predicted, so as stated it is not yet falsifiable (open problem M7: needs an upper bound or a capacity-scaling law).
3. **Observer-density effects** — requires an operational observer criterion and pre-registration; the Global Consciousness Project record counts against an easy-to-detect effect.
4. **Black-hole information** — information preservation is already the mainstream expectation (Page curve, island formula). A distinctive claim would be a departure from the Page curve. No mechanism yet.
5. **Mathematical limits** — not falsifiable; moved to philosophy.
6. **Decoherence asymmetry** — the quantum Zeno effect already covers "measured vs. isolated." Only a conscious-vs-device difference with identical physical couplings would be distinctive.

---

## Equation checks

```
pip install sympy numpy
python3 tools/equation_checks.py
```

The script checks the free-index balance and SI units of every displayed equation, recomputes every quoted number from CODATA 2018, confirms as a bookkeeping check that the proposed equation collapses to Einstein's when the hidden-space terms vanish, and documents why the v2.1 "master equation" was removed. It is a sanity check, not a derivation — the derivation is the Kaluza–Klein reduction in THEORY.md §3.3.

---

## Contributing and feedback

- **Found a flaw, a wrong citation, or a claim that is not tagged honestly?** [Open an Issue](https://github.com/JBG-32/substratum-theory/issues/new).
- **Want to propose a model for an open problem, argue the philosophy, or ask something?** [Suggest an improvement](https://github.com/JBG-32/substratum-theory/issues/new?template=suggestion.yml) or [ask a question](https://github.com/JBG-32/substratum-theory/issues/new?template=question.yml).

> **How replies work:** an AI assistant reads new feedback and replies first, on behalf of Juan Hinojosa, and says plainly that it is an AI. Anything that asks for Juan's own reply or decision is labelled `needs-juan` and passed to him.
- See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Open Problems](THEORY.md#part-xi-known-limitations-and-open-problems) list in THEORY.md.

The most valuable contributions right now, in order: a toy model for the hidden manifold (Σ₈ = T⁸ with one scalar field); a Lorentz-invariant "finite resolution" model; a pre-registered protocol for Prediction 6; a multipole-analysis proposal for Prediction 1.

---

## Epistemic Status

**Speculative.** Not peer-reviewed physics. The document distinguishes, line by line, what is established, what is hypothesis, and what is speculation. Several claims from v1.0–v2.1 were withdrawn in v3.0 because they conflicted with data or were not well-formed.

---

## Live Site

https://jbg-32.github.io/substratum-theory/ (GitHub Pages)

---

## License

[Creative Commons Attribution 4.0 International](LICENSE). Share and adapt freely with attribution.

---

## Author

**Juan Hinojosa** — developed with assistance from Claude, an AI model by Anthropic. The AI assistance does not imply endorsement by Anthropic.

---

*"The door to D12, if there is one, is still in the equations. They now have to be the right equations."*
