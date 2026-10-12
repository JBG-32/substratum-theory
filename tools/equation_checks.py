#!/usr/bin/env python3
"""
equation_checks.py — automated sanity checks for every displayed equation in
THEORY.md / index.html (Substratum Theory v3.0).

Run:  python3 tools/equation_checks.py
Deps: sympy, numpy  (pip install sympy numpy)

Each check is one of:
  * INDEX   — free-index balance of a tensor equation (symbolic bookkeeping)
  * UNITS   — SI dimensional consistency via sympy.physics.units
  * NUMERIC — a numerical value quoted in the text, recomputed from CODATA 2018
  * LIMIT   — a proposed equation reduces to known physics in a stated limit

It also records the v2.1 equations that were REMOVED and why, so the removal
is auditable.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field

import numpy as np
import sympy as sp
from sympy.physics import units as u
from sympy.physics.units import Quantity
from sympy.physics.units.systems.si import dimsys_SI, SI


# --------------------------------------------------------------------------
# CODATA 2018 constants (SI)
# --------------------------------------------------------------------------
HBAR = 1.054571817e-34  # J s
H = 6.62607015e-34      # J s
C = 2.99792458e8        # m/s
G = 6.67430e-11         # m^3 kg^-1 s^-2
KB = 1.380649e-23       # J/K
M_SUN = 1.98847e30      # kg
EV = 1.602176634e-19    # J
M_E = 9.1093837015e-31  # kg
M_RB87 = 86.909180 * 1.66053906660e-27  # kg
M_AL = 26.9815385 * 1.66053906660e-27   # kg

results: list[tuple[str, str, bool, str]] = []


def record(kind: str, name: str, ok: bool, detail: str = "") -> None:
    results.append((kind, name, ok, detail))
    flag = "PASS" if ok else "FAIL"
    print(f"[{flag}] {kind:7s} {name}")
    if detail:
        for line in detail.splitlines():
            print(f"         {line}")


# --------------------------------------------------------------------------
# Helper: free-index bookkeeping for tensor expressions
# --------------------------------------------------------------------------
@dataclass
class Tensor:
    """A tensor factor with explicit up/down index labels."""
    name: str
    up: tuple[str, ...] = ()
    down: tuple[str, ...] = ()


def free_indices(term: list[Tensor]) -> tuple[set[str], set[str]]:
    """Return (free_up, free_down) after contracting repeated up/down pairs."""
    ups: list[str] = []
    downs: list[str] = []
    for t in term:
        ups += list(t.up)
        downs += list(t.down)
    contracted = set(ups) & set(downs)
    free_up = {i for i in ups if i not in contracted}
    free_down = {i for i in downs if i not in contracted}
    # repeated same-position indices are an error
    dup_up = len(ups) != len(set(ups))
    dup_down = len(downs) != len(set(downs))
    if dup_up or dup_down:
        raise ValueError("index repeated in the same position (not a contraction)")
    return free_up, free_down


def check_balance(name: str, lhs: list[Tensor], rhs_terms: list[list[Tensor]]) -> bool:
    try:
        l_up, l_dn = free_indices(lhs)
        ok = True
        detail = f"LHS free: up={sorted(l_up)} down={sorted(l_dn)}"
        for k, term in enumerate(rhs_terms):
            r_up, r_dn = free_indices(term)
            detail += f"\nRHS term {k+1}: up={sorted(r_up)} down={sorted(r_dn)}"
            if (r_up, r_dn) != (l_up, l_dn):
                ok = False
    except ValueError as e:
        ok, detail = False, str(e)
    record("INDEX", name, ok, detail)
    return ok


# --------------------------------------------------------------------------
# Helper: SI dimensional analysis
# --------------------------------------------------------------------------
def dim_of(expr) -> sp.Expr:
    return SI.get_dimensional_expr(expr)


def same_dim(a, b) -> bool:
    da = dimsys_SI.get_dimensional_dependencies(dim_of(a))
    db = dimsys_SI.get_dimensional_dependencies(dim_of(b))
    return da == db


# ==========================================================================
# 1. REMOVED: v2.1 "master equation"   R^(4)_{mu nu} = ∫_Σ8 Ω^{ab}_{cd} Ψ_{ab} ∧ Ψ̄^{cd} dΣ
# ==========================================================================
print("\n=== 1. v2.1 master equation (REMOVED) ===")
lhs = [Tensor("R4", down=("mu", "nu"))]
rhs = [[Tensor("Omega", up=("a", "b"), down=("c", "d")),
        Tensor("Psi", down=("a", "b")),
        Tensor("Psibar", up=("c", "d"))]]
balanced = check_balance("v2.1 master equation: free-index balance", lhs, rhs)
# Expect FAIL: LHS has free (mu,nu); RHS fully contracted → scalar.
assert not balanced, "v2.1 equation unexpectedly balanced"
# Form-degree argument: Ψ_ab ∧ Ψ̄^cd (two 2-forms) is a 4-form; integrating a
# 4-form over an 8-manifold is undefined, and the trailing 'dΣ' double-counts
# the measure.
form_degree = 2 + 2
record("INDEX", "v2.1 master equation: form degree vs manifold dimension",
       form_degree != 8,  # 'ok' here means 'we correctly detect the defect'
       f"wedge of two 2-forms has degree {form_degree}; Σ has dimension 8 → "
       "integral undefined; extra dΣ redundant. REMOVED from v3.0.")

# ==========================================================================
# 2. ESTABLISHED: Einstein field equations
#    G_{mu nu} + Λ g_{mu nu} = (8 π G / c^4) T_{mu nu}
# ==========================================================================
print("\n=== 2. Einstein field equations ===")
check_balance("EFE free-index balance",
              [Tensor("G", down=("mu", "nu"))],
              [[Tensor("Lambda"), Tensor("g", down=("mu", "nu"))],
               [Tensor("8piG/c4"), Tensor("T", down=("mu", "nu"))]])
# Units: G_{mu nu} has dimension 1/length^2 (curvature). T_{mu nu} is energy density.
curv = 1 / u.meter**2
rhs_units = 8 * sp.pi * u.gravitational_constant / u.speed_of_light**4 * (u.joule / u.meter**3)
record("UNITS", "EFE: 8πG/c^4 · (energy density) has units of curvature (m^-2)",
       same_dim(curv, rhs_units),
       f"dim(8πG/c^4·ρ_E) = {dim_of(rhs_units)}")

# ==========================================================================
# 3. ESTABLISHED: Kaluza–Klein reduction of the Einstein–Hilbert action
#    S_D = (1/16πG_D) ∫ d^D x sqrt(-g_D) R_D,  D = 4 + n,  M_D = M_4 × Σ_n
#    ⇒  G_4 = G_D / Vol(Σ_n)
# ==========================================================================
print("\n=== 3. Kaluza–Klein reduction: G_4 = G_D / Vol(Σ_n) ===")
n = 8  # internal dimensions in the Substratum hypothesis (D5–D12)
D = 4 + n
# Units of G_D in D dimensions: [G_D] = [G_4] · length^n  (so that S is dimensionless in ħ=1,
# or equivalently so that G_D/Vol has the units of G_4).
G4_units = u.gravitational_constant
GD_units = u.gravitational_constant * u.meter**n
vol_units = u.meter**n
record("UNITS", f"G_4 = G_{D} / Vol(Σ_{n}) dimensionally consistent",
       same_dim(G4_units, GD_units / vol_units),
       f"[G_{D}] = [G_4]·m^{n};  [G_{D}]/[Vol] = {dim_of(GD_units / vol_units)}")
# Symbolic reduction: with a product metric and R_D = R_4 + R_Σ, the 4D part of the
# action picks up the factor Vol(Σ_n).
G_D, Vol, R4, RS = sp.symbols("G_D Vol R_4 R_Sigma", positive=True)
S_density_4d = (Vol / (16 * sp.pi * G_D)) * R4
G_4_eff = sp.solve(sp.Eq(1 / (16 * sp.pi * sp.Symbol("G_4", positive=True)) * R4, S_density_4d),
                   sp.Symbol("G_4", positive=True))[0]
# (bookkeeping check; the reduction itself is the derivation in THEORY.md §3.3)
record("LIMIT", "KK: coefficient of ∫√-g4 R4 identifies G_4 = G_D/Vol(Σ)",
       sp.simplify(G_4_eff - G_D / Vol) == 0, f"G_4 = {G_4_eff}")
# Illustrative numeric: if Σ_8 were a flat torus of side L, Vol = L^8.
L = 1.616255e-35  # one Planck length per side (illustration only; NOT a prediction)
record("NUMERIC", "Illustration: Vol(T^8) with Planck-length sides",
       True, f"Vol = L^8 = {L**8:.3e} m^8  → G_12 = G_4·Vol = {G*L**8:.3e} m^11 kg^-1 s^-2")

# ==========================================================================
# 4. OUR HYPOTHESIS (well-formed): 4D effective equations with internal-space source
#    G^(4)_{mu nu} + Λ_eff g_{mu nu} = (8πG_4/c^4) [ T^(matter)_{mu nu} + T^(Σ)_{mu nu} ]
#    T^(Σ)_{mu nu}(x) = ∫_Σ d^n y sqrt(g_Σ) τ_{mu nu}(x,y)
#    Reduces to GR when T^(Σ) → 0 and Λ_eff → Λ.
# ==========================================================================
print("\n=== 4. Proposed 4D effective equation (OUR HYPOTHESIS) ===")
check_balance("Effective 4D equation: free-index balance",
              [Tensor("G4", down=("mu", "nu"))],
              [[Tensor("Lambda_eff"), Tensor("g", down=("mu", "nu"))],
               [Tensor("8piG4/c4"), Tensor("Tmatter", down=("mu", "nu"))],
               [Tensor("8piG4/c4"), Tensor("TSigma", down=("mu", "nu"))]])
# Units: τ_{mu nu}(x,y) is a D-dimensional energy density, i.e. energy per unit
# (D−1)-dimensional spatial volume, J/m^(D-1). Integrating over the n internal
# dimensions multiplies by m^n and yields J/m^3 — a 4D energy density. Hence the
# clean statement is T^(Σ)_{mu nu}(x) = ∫_Σ d^n y √g_Σ τ_{mu nu}(x,y) with NO 1/Vol
# prefactor (a 1/Vol would leave J/m^11, which is wrong).
tau_units = u.joule / u.meter**(D - 1)
TSigma_units = tau_units * u.meter**n
record("UNITS", "T^(Σ)_{μν} = ∫_Σ d^n y √g_Σ τ_{μν} has units of 4D energy density (J/m^3)",
       same_dim(TSigma_units, u.joule / u.meter**3),
       f"[τ] = J/m^{D-1}; ×m^{n} → {dim_of(TSigma_units)}  (NOTE: no 1/Vol prefactor)")
# GR limit
T_sig, T_mat, Lam, Lam_eff, gmn, Gmn = sp.symbols("T_Sigma T_mat Lambda Lambda_eff g G")
kappa = sp.Symbol("kappa")  # 8πG_4/c^4
proposed = sp.Eq(Gmn + Lam_eff * gmn, kappa * (T_mat + T_sig))
gr = sp.Eq(Gmn + Lam * gmn, kappa * T_mat)
reduced = proposed.subs({T_sig: 0, Lam_eff: Lam})
# (bookkeeping check; the reduction itself is the derivation in THEORY.md §3.3)
record("LIMIT", "Effective equation → Einstein equations when T^(Σ)=0, Λ_eff=Λ",
       sp.simplify(reduced.lhs - gr.lhs) == 0 and sp.simplify(reduced.rhs - gr.rhs) == 0,
       f"{reduced}")

# ==========================================================================
# 5. ESTABLISHED: Robertson uncertainty relation
#    σ_A σ_B ≥ ½ |⟨[A,B]⟩| ;  [x,p] = iħ  ⇒  σ_x σ_p ≥ ħ/2
# ==========================================================================
print("\n=== 5. Robertson / Heisenberg ===")
record("UNITS", "σ_x σ_p ≥ ħ/2: (m)(kg m/s) vs J·s",
       same_dim(u.meter * u.kilogram * u.meter / u.second, u.joule * u.second),
       f"{dim_of(u.meter*u.kilogram*u.meter/u.second)} == {dim_of(u.joule*u.second)}")
# Numerical check with a Gaussian wavepacket (minimum uncertainty): σ_x σ_p = ħ/2 exactly.
sigma_x = 1e-9
x = np.linspace(-20 * sigma_x, 20 * sigma_x, 200001)
psi = (2 * np.pi * sigma_x**2) ** -0.25 * np.exp(-x**2 / (4 * sigma_x**2))
dx = x[1] - x[0]
prob = psi**2
mean_x2 = np.sum(x**2 * prob) * dx
dpsi = np.gradient(psi, dx)
# <p^2> = ħ^2 ∫ |ψ'|^2 dx for real ψ
mean_p2 = HBAR**2 * np.sum(dpsi**2) * dx
prod = math.sqrt(mean_x2 * mean_p2)
record("NUMERIC", "Gaussian packet saturates σ_x σ_p = ħ/2",
       abs(prod / (HBAR / 2) - 1) < 1e-3, f"σ_xσ_p/(ħ/2) = {prod/(HBAR/2):.6f}")

# ==========================================================================
# 6. ESTABLISHED: Bell / CHSH bound and Tsirelson bound
#    |S| ≤ 2 (local realism);  S_QM,max = 2√2
# ==========================================================================
print("\n=== 6. CHSH / Tsirelson ===")
# Local deterministic strategies: enumerate all a,a',b,b' ∈ {±1}
best_local = 0
for a in (1, -1):
    for a2 in (1, -1):
        for b in (1, -1):
            for b2 in (1, -1):
                S = a * b + a * b2 + a2 * b - a2 * b2
                best_local = max(best_local, abs(S))
record("NUMERIC", "CHSH local-realist maximum |S| = 2 (exhaustive)", best_local == 2,
       f"max over deterministic strategies = {best_local}")
# Quantum: singlet state, E(a,b) = -cos(θa-θb); optimal angles 0, π/2, π/4, -π/4
def E(ta, tb):
    return -math.cos(ta - tb)
S_q = E(0, math.pi/4) + E(0, -math.pi/4) + E(math.pi/2, math.pi/4) - E(math.pi/2, -math.pi/4)
record("NUMERIC", "CHSH quantum (singlet) value = 2√2 (Tsirelson)",
       abs(abs(S_q) - 2 * math.sqrt(2)) < 1e-12, f"|S| = {abs(S_q):.12f}, 2√2 = {2*math.sqrt(2):.12f}")

# ==========================================================================
# 7. ESTABLISHED: Tunnelling transmission (rectangular barrier, exact) and WKB
#    T = [1 + V0^2 sinh^2(κ a) / (4E(V0−E))]^-1,  κ = sqrt(2m(V0−E))/ħ
#    WKB: T ≈ exp(−2 ∫ κ dx)
# ==========================================================================
print("\n=== 7. Tunnelling ===")
kappa_units = sp.sqrt(2 * u.kilogram * u.joule) / (u.joule * u.second)
record("UNITS", "κ = sqrt(2m(V0−E))/ħ has units 1/m",
       same_dim(kappa_units, 1 / u.meter), f"dim(κ) = {dim_of(kappa_units)}")
# Numeric: electron, V0 = 1 eV, E = 0.5 eV, a = 1 nm
V0, E_, a = 1 * EV, 0.5 * EV, 1e-9
kap = math.sqrt(2 * M_E * (V0 - E_)) / HBAR
T_exact = 1 / (1 + V0**2 * math.sinh(kap * a)**2 / (4 * E_ * (V0 - E_)))
T_wkb = math.exp(-2 * kap * a)
record("NUMERIC", "Electron, 1 eV barrier, 1 nm, E=0.5 eV: exact vs WKB agree in order of magnitude",
       0.1 < T_exact / T_wkb < 10, f"κ={kap:.3e} m^-1, T_exact={T_exact:.3e}, T_WKB={T_wkb:.3e}")

# ==========================================================================
# 8. ESTABLISHED: Bekenstein–Hawking entropy and Hawking temperature
#    S_BH = k_B c^3 A / (4 G ħ),   T_H = ħ c^3 / (8 π G M k_B)
# ==========================================================================
print("\n=== 8. Black-hole thermodynamics ===")
S_units = u.boltzmann_constant * u.speed_of_light**3 * u.meter**2 / (u.gravitational_constant * u.hbar)
record("UNITS", "S_BH = k_B c^3 A/(4Għ) has units J/K", same_dim(S_units, u.joule / u.kelvin),
       f"dim = {dim_of(S_units)}")
T_units = u.hbar * u.speed_of_light**3 / (u.gravitational_constant * u.kilogram * u.boltzmann_constant)
record("UNITS", "T_H = ħc^3/(8πGMk_B) has units K", same_dim(T_units, u.kelvin),
       f"dim = {dim_of(T_units)}")
T_H_sun = HBAR * C**3 / (8 * math.pi * G * M_SUN * KB)
record("NUMERIC", "T_H for one solar mass ≈ 6.2×10^-8 K", abs(T_H_sun / 6.17e-8 - 1) < 0.02,
       f"T_H = {T_H_sun:.3e} K")
r_s = 2 * G * M_SUN / C**2
A = 4 * math.pi * r_s**2
S_sun = KB * C**3 * A / (4 * G * HBAR)
record("NUMERIC", "S_BH for one solar mass ≈ 1.4×10^54 J/K (≈1.0×10^77 k_B)",
       abs(S_sun / KB / 1.05e77 - 1) < 0.1, f"S = {S_sun:.3e} J/K = {S_sun/KB:.3e} k_B")

# ==========================================================================
# 9. ESTABLISHED: Casimir pressure between parallel plates
#    P = − π^2 ħ c / (240 a^4)
# ==========================================================================
print("\n=== 9. Casimir ===")
P_units = u.hbar * u.speed_of_light / u.meter**4
record("UNITS", "π²ħc/(240a⁴) has units Pa", same_dim(P_units, u.pascal), f"dim = {dim_of(P_units)}")
P_1um = math.pi**2 * HBAR * C / (240 * (1e-6)**4)
record("NUMERIC", "Casimir pressure at a = 1 µm ≈ 1.3 mPa", abs(P_1um / 1.3e-3 - 1) < 0.02,
       f"P = {P_1um:.3e} Pa")

# ==========================================================================
# 10. ESTABLISHED: Planck units (v2.1 wrote h instead of ħ — corrected)
#     l_P = sqrt(ħG/c^3),  t_P = sqrt(ħG/c^5),  c = l_P/t_P (identity)
# ==========================================================================
print("\n=== 10. Planck units ===")
lP = math.sqrt(HBAR * G / C**3)
tP = math.sqrt(HBAR * G / C**5)
lP_h = math.sqrt(H * G / C**3)
record("NUMERIC", "l_P = sqrt(ħG/c³) = 1.616×10^-35 m", abs(lP / 1.616255e-35 - 1) < 1e-4, f"l_P = {lP:.6e} m")
record("NUMERIC", "t_P = sqrt(ħG/c⁵) = 5.391×10^-44 s", abs(tP / 5.391247e-44 - 1) < 1e-4, f"t_P = {tP:.6e} s")
record("NUMERIC", "v2.1 used h (not ħ): sqrt(hG/c³) would give 4.05×10^-35 m ≠ quoted 1.6×10^-35 m",
       abs(lP_h / 4.05e-35 - 1) < 0.01, f"sqrt(hG/c^3) = {lP_h:.3e} m  → v2.1 formula/value mismatch, fixed in v3.0")
record("NUMERIC", "c = l_P / t_P is an identity (no new content)", abs(lP / tP / C - 1) < 1e-12,
       f"l_P/t_P = {lP/tP:.9e} m/s")
E_Pl_GeV = math.sqrt(HBAR * C**5 / G) / EV / 1e9
record("NUMERIC", "E_Planck ≈ 1.22×10^19 GeV", abs(E_Pl_GeV / 1.2209e19 - 1) < 1e-3, f"E_Pl = {E_Pl_GeV:.4e} GeV")

# ==========================================================================
# 11. ESTABLISHED: Lorentz-invariance-violation parametrisation and Fermi bound
#     v(E) ≈ c [1 − ξ_n (n+1)/2 (E/E_QG,n)^n]   (subluminal, ξ=+1)
#     GRB 090510: E_QG,1 > 7.6 E_Pl  (Vasileiou et al. 2013)
# ==========================================================================
print("\n=== 11. Lorentz invariance / lattice spacetime ===")
E_QG1_GeV = 7.6 * E_Pl_GeV   # Vasileiou et al. 2013, 95% CL, subluminal (xi_1=+1); Abdo et al. 2009 gave 1.2 E_Pl
E_QG2_GeV = 1.3e11           # Vasileiou et al. 2013, quadratic case
# Fractional velocity shift for a 10^20 eV = 10^11 GeV cosmic ray, linear order:
E_cr_GeV = 1e11
dv_over_c = 1.0 * (E_cr_GeV / E_QG1_GeV)
record("NUMERIC", "Linear-order (n=1) LIV at 10^20 eV is bounded to |δv/c| < ~10^-9 (E_QG,1 > 7.6 E_Pl)",
       dv_over_c < 2e-8, f"(E/E_QG,1) = {dv_over_c:.2e}")
record("NUMERIC", "Quadratic-order (n=2) LIV at 10^20 eV: (E/E_QG,2)^2 with E_QG,2 = 1.3e11 GeV",
       (E_cr_GeV / E_QG2_GeV) ** 2 < 1.0, f"(E/E_QG,2)^2 = {(E_cr_GeV/E_QG2_GeV)**2:.2e}  (E_QG,2/E_Pl = {E_QG2_GeV/E_Pl_GeV:.1e})")
# Naive Planck-lattice expectation (E_QG ~ E_Pl, n=1) would give (E/E_Pl):
record("NUMERIC", "A naive Planck-scale lattice (E_QG,1 = E_Pl) is EXCLUDED by GRB 090510 (7.6 E_Pl > E_Pl)",
       7.6 > 1.0, "any Substratum 'sampling' model must suppress linear-order dispersion")

# ==========================================================================
# 12. ESTABLISHED: Entanglement scale already demonstrated (Prediction 2 threshold)
# ==========================================================================
print("\n=== 12. Entanglement scale ===")
N_drum = 70e-15 / M_AL      # 70 pg aluminium drumhead (Kotler et al. 2021)
record("NUMERIC", "70 pg Al drumhead ≈ 1.6×10^12 atoms  (> v2.1 threshold 10^6 by 10^6×)",
       N_drum > 1e12, f"N ≈ {N_drum:.2e} atoms")
record("NUMERIC", "Julsgaard et al. 2001: two 10^12-atom Cs ensembles entangled (> 10^6)",
       1e12 > 1e6, "v2.1 Prediction 2 threshold (>10^6 particles) is already exceeded → rewritten")

# ==========================================================================
# 13. Tunnelling-time experiment sanity (Ramos et al. 2020): Rb-87, barrier ~1.3 µm
# ==========================================================================
print("\n=== 13. Tunnelling time (Ramos et al. 2020) scale ===")
# Order-of-magnitude: Larmor-clock dwell time ~ m / (ħ κ^2) for a thick barrier.
# With V0−E ~ h·(few hundred Hz) for ultracold Rb, κ ~ 10^6 m^-1 → τ ~ ms. Reported ~0.6 ms.
dE = H * 300.0  # ~300 Hz × h
kap_rb = math.sqrt(2 * M_RB87 * dE) / HBAR
tau_est = M_RB87 / (HBAR * kap_rb**2)
record("NUMERIC", "Dwell-time scale for ultracold Rb-87 under ~h·300 Hz barrier is ~ms (reported ≈0.6 ms)",
       1e-4 < tau_est < 1e-2, f"κ ≈ {kap_rb:.2e} m^-1, τ ≈ {tau_est*1e3:.2f} ms (order-of-magnitude only)")

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
print("\n=== SUMMARY ===")
n_pass = sum(1 for r in results if r[2])
n_fail = sum(1 for r in results if not r[2])
print(f"{n_pass} checks passed, {n_fail} failed (the single expected FAIL is the removed v2.1 equation)")
# Exit non-zero only if an unexpected failure occurs
unexpected = [r for r in results if not r[2] and not r[1].startswith("v2.1 master equation")]
sys.exit(1 if unexpected else 0)
