# Bradley Continuum Wave Mechanics - Verification and Stress-Test Workbench

An interactive, client-side physics verification app built with Streamlit to:
1. **Demonstrate Bradley Continuum Wave Mechanics** across galactic, stellar, compact-object, and cosmological scales with **zero per-system free parameters (N_fit = 0)**.
2. **Expose cross-domain parameter tensions in Lambda-CDM**, showing how tuning or adjusting model parameters for one observational regime creates conflicts or extra degrees of freedom in others.

## Framework Overview

Bradley Continuum Wave Mechanics formulates wave transport on static three-dimensional Euclidean space with a flat Minkowski metric eta_mu_nu = diag(-1, 1, 1, 1) (G_mu_nu = 0), modeling gravity, refraction, matter solitons, and cosmological redshift through a dielectric-elastic scalar continuum and wave attenuation rather than curved spacetime expansion or dark matter halos.

### Core Constants and Derived Scales (N_fit = 0)
* **Fundamental constants:** c_0 = 299,792,458 m/s, G = 6.67430e-11 m^3/kg/s^2, h = 6.62607015e-34 J*s, m_e = 9.1093837e-31 kg.
* **Attenuation and acoustic baseline inputs:** H_0 = 67.40 km/s/Mpc, r_s = 147.09 Mpc, and canonical SPARC mass-to-light priors ((M/L)_disk = 0.50, (M/L)_bulge = 0.70).
* **Derived continuum scales:**
  * Kinematic acceleration floor: a_B = c_0 * H_0 / (2*pi) = 1.0422e-10 m/s^2
  * Attenuation length: D_att = c_0 / H_0 = 4,448.0 Mpc
  * Electron Compton frequency: f_e = m_e * c_0^2 / h = 1.2356e20 Hz

## What the App Does (7 Interactive Modes)

1. **SPARC Galactic Disks (N = 175):** Predicts rotation curves forward from baryonic mass profiles (gas, disk, bulge) using hydrostatic vertical confinement eta = exp(-kappa) and the Bradley acceleration law. Includes catalog filters (full 175 catalog, HSB giants, LSB dwarfs, dwarf irregulars) and a diagnostic (M/L)_disk slider.
2. **Gaia DR3 Wide Binaries:** Models unconfined 3D point-mass pairs (eta = 0) with 2D-to-3D deprojection, showing the transition across the Rene radius s_R and saturation at gamma -> sqrt(2) = 1.414 against Gaia DR3 benchmarks.
3. **Pantheon+ Supernovae and Pulse Dilation:** Compares static Euclidean luminosity distance D_L(z) = D_att * ln(1+z) * (1+z) against Pantheon+ data (published mu_SH0ES vs. low-z-anchored m_B) and includes an interactive wave-packet elongation simulator (dt_obs = dt_emit * (1+z)).
4. **DESI BAO Standard Ruler (7 Bins):** Evaluates transverse (D_M/r_s), radial (D_H/r_s), and volume-averaged (D_V/r_s) acoustic ratios across the seven DESI DR1 tracer bins with N_fit = 0.
5. **Compact Cores and Acoustic Echoes:** Explores non-singular dielectric cores bounded by the Gray limit (r_Gray = 0.5 * r_g, Phi_Gray = 2), spin-dependent photon spheres, shadow size (2e * r_g = 5.437 * r_g, +4.63% vs. GR), core ringing frequency, and cavity echo recurrence delays.
6. **Coupled System Stress-Test (Lambda-CDM vs. Bradley):** Side-by-side 4-panel comparison and live constraint ledger across SPARC rotation curves (NGC3198), wide binaries (analytically tied to halo density at R_solar = 8.2 kpc), Pantheon+ residuals at z = 1.02, and JWST z=10 disk diameters, plus comparisons for core gravity profiles, Earth flybys, and the cosmic matter dipole.
7. **Vulnerability Audit and Defense:** Walks through key empirical challenges - HSB vs. LSB residuals, wide binary triple/RUWE debates, static-space light-curve stretching, DESI transverse scaling, and LIGO echo / ngEHT shadow tests.

## Demonstrating Lambda-CDM Cross-Domain Tensions

In **Mode 6**, you can adjust Lambda-CDM parameters - halo type (Pseudo-Isothermal vs. NFW), halo velocity and scale radius, disk/bulge M/L, inclination shift delta_i, Omega_Lambda, and H_0 - or trigger preset scenarios. Tuning a dark matter halo or cosmological parameter to improve a fit in one regime carries direct consequences in the coupled panels (such as near-unity wide-binary boost from local halo density or shifts in implied early-universe disk sizes), illustrating why the site pairs forward continuum predictions with cross-domain stress tests.

## Scope, Limitations and Falsification Tests

* **Declared inputs vs. derivations:** While core field and optical relations follow from the action, quantities such as H_0, r_s, stellar-vacuum power density, and alpha enter as constitutive or empirical inputs rather than closed-form mechanical eigenvalues.
* **Quantitative caveats:** Unadjusted zero-parameter curves show higher chi-squared / residuals in massive HSB/bulged galaxies under fixed M/L and systematic offsets in DESI BAO bins - details documented transparently in the app and manuscripts.
* **Key observational tests:** Next-generation EHT shadow measurements (+4.63% prediction), high-SNR gravitational-wave ringdown echo searches, Gaia DR4/DR5 wide-binary purity studies, and high-Q SRF cavity tests.

## Running Locally

Place `app.py`, `all_sparc_galaxies.txt`, and `pantheon_compact.csv` in the same directory, install `streamlit`, `numpy`, and `matplotlib`, and run:

```bash
streamlit run app.py