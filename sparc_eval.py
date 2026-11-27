import os
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==============================================================================
# SECTION 1: PHYSICAL CONSTANTS & DERIVED SCALES (N_fit = 0)
# ==============================================================================
c_0 = 299792458.0                  # Speed of light in vacuum (m/s) [CODATA 2022]
G = 6.67430e-11                    # Gravitational constant (m^3 kg^-1 s^-2) [CODATA 2022]
H_0_kmsMpc = 67.40                  # Hubble constant (km/s/Mpc) [Planck 2018 CMB]
Mpc_in_m = 3.08567758149137e22      # Meters per Megaparsec
kpc_in_m = 3.08567758149137e19      # Meters per Kiloparsec
G_astro = 4.3009e-3                # G in pc * (km/s)^2 / M_sun

# Fundamental acceleration floor derived forward from horizon phase relaxation:
H_0_SI = (H_0_kmsMpc * 1000.0) / Mpc_in_m   # 2.184285e-18 s^-1
a_B = (c_0 * H_0_SI) / (2.0 * np.pi)        # 1.042198e-10 m/s^2

# Canonical Photometric Mass-to-Light Ratios (Spitzer 3.6 um band, Lelli et al. 2016)
ML_DISK = 0.50
ML_BULGE = 0.70
SIGMA_GAS_DEFAULT = 8.0  # km/s

# ==============================================================================
# SECTION 2: THE BRADLEY ACCELERATION LAW
# ==============================================================================
def bradley_acceleration(g_N, eta):
    """
    Bradley Acceleration Law:
      g_total = sqrt( g_N^2 + eta * a_B * g_N + (1 - eta) * g_N^2 * tanh(a_B / g_N) )
    """
    g_N_clean = np.maximum(g_N, 1e-25)
    ratio = a_B / g_N_clean
    g_total_sq = g_N**2 + eta * a_B * g_N + (1.0 - eta) * (g_N**2) * np.tanh(ratio)
    return np.sqrt(np.maximum(g_total_sq, 0.0))

def estimate_disk_scale_length_kpc(r_kpc, v_disk_s, sb_disk=None):
    if sb_disk is not None and len(sb_disk) >= 3 and sb_disk[0] > 0:
        valid_sb = sb_disk > 0
        if np.sum(valid_sb) >= 3:
            r_v = r_kpc[valid_sb]
            sb_v = sb_disk[valid_sb]
            target_sb = sb_v[0] / np.e
            if sb_v[-1] <= target_sb:
                for idx in range(len(sb_v) - 1):
                    if sb_v[idx] >= target_sb >= sb_v[idx + 1]:
                        frac = (sb_v[idx] - target_sb) / max(sb_v[idx] - sb_v[idx + 1], 1e-12)
                        return max(r_v[idx] + frac * (r_v[idx + 1] - r_v[idx]), 0.25)

    if len(v_disk_s) > 0 and np.max(v_disk_s) > 0:
        idx_peak = np.argmax(v_disk_s)
        if r_kpc[idx_peak] > 0:
            return max(r_kpc[idx_peak] / 2.15, 0.25)

    return max(np.max(r_kpc) / 3.2, 0.25)

def evaluate_galaxy_bradley(r_kpc, v_obs, v_err, v_gas, v_disk, v_bul, sb_disk=None, sb_bul=None):
    r_m = r_kpc * kpc_in_m
    v_err_clean = np.maximum(v_err, 0.5)

    v_disk_s = np.sqrt(ML_DISK) * v_disk
    v_bul_s = np.sqrt(ML_BULGE) * v_bul

    # Total baryonic circular velocity
    v_bar_sq = np.abs(v_gas) * v_gas + (v_disk_s**2) + (v_bul_s**2)
    v_bar_sq_pos = np.maximum(v_bar_sq, 0.0)
    g_N = (v_bar_sq_pos * 1e6) / r_m

    # Vertical scale height z0 and aspect ratio kappa
    if sb_disk is not None and len(sb_disk) > 0 and np.max(sb_disk) > 0:
        sb_total = ML_DISK * sb_disk + (ML_BULGE * sb_bul if sb_bul is not None else 0.0)
        sigma_0 = max(np.max(sb_total), 1.0)
    else:
        sigma_0 = max(np.max(v_bar_sq_pos) / (2.0 * np.pi * G_astro * max(r_kpc[0], 0.5) * 1000.0), 5.0)

    z0_pc = (SIGMA_GAS_DEFAULT**2) / (2.0 * np.pi * G_astro * sigma_0)
    z0_kpc = z0_pc / 1000.0
    Rd_kpc = estimate_disk_scale_length_kpc(r_kpc, v_disk_s, sb_disk)
    kappa = z0_kpc / Rd_kpc
    eta = np.exp(-kappa)

    # Bradley prediction
    g_total = bradley_acceleration(g_N, eta)
    v_pred = np.sqrt((g_total * r_m) / 1e6)

    res = v_obs - v_pred
    chi2_red = np.mean((res / v_err_clean)**2)

    return {
        'r': r_kpc,
        'v_obs': v_obs,
        'v_err': v_err,
        'v_bar': np.sqrt(v_bar_sq_pos),
        'v_pred': v_pred,
        'res': res,
        'chi2_red': chi2_red,
        'eta': eta,
        'kappa': kappa,
        'Rd_kpc': Rd_kpc,
        'z0_pc': z0_pc
    }

def load_sparc_database(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    blocks = re.split(r'===\s*([A-Za-z0-9\-_]+)_rotmod\.dat\s*===', text)
    galaxies = {}

    for i in range(1, len(blocks), 2):
        name = blocks[i].strip()
        data_text = blocks[i+1].strip()

        lines = [l.strip() for l in data_text.split('\n') if l.strip()]
        dist_mpc = None
        rad, vobs, errv, vgas, vdisk, vbul, sbdisk, sbbul = [], [], [], [], [], [], [], []

        for line in lines:
            if line.startswith('#'):
                if 'Distance' in line and '=' in line:
                    try:
                        dist_mpc = float(line.split('=')[1].replace('Mpc', '').strip())
                    except:
                        pass
                continue

            parts = line.split()
            if len(parts) >= 6:
                try:
                    r = float(parts[0])
                    vo = float(parts[1])
                    ev = float(parts[2])
                    vg = float(parts[3])
                    vd = float(parts[4])
                    vb = float(parts[5])
                    sbd = float(parts[6]) if len(parts) > 6 else 0.0
                    sbb = float(parts[7]) if len(parts) > 7 else 0.0

                    rad.append(r)
                    vobs.append(vo)
                    errv.append(ev)
                    vgas.append(vg)
                    vdisk.append(vd)
                    vbul.append(vb)
                    sbdisk.append(sbd)
                    sbbul.append(sbb)
                except:
                    continue

        if len(rad) >= 3:
            galaxies[name] = {
                'name': name,
                'dist_mpc': dist_mpc,
                'rad': np.array(rad),
                'vobs': np.array(vobs),
                'errv': np.array(errv),
                'vgas': np.array(vgas),
                'vdisk': np.array(vdisk),
                'vbul': np.array(vbul),
                'sbdisk': np.array(sbdisk),
                'sbbul': np.array(sbbul)
            }
    return galaxies

if __name__ == '__main__':
    catalog = load_sparc_database('/workspace/knowledge/all_sparc_galaxies.txt')
    print(f"Loaded {len(catalog)} galaxies from SPARC aggregated catalog.")
    chi2_list = []
    for name, g in catalog.items():
        res = evaluate_galaxy_bradley(
            g['rad'], g['vobs'], g['errv'], g['vgas'], g['vdisk'], g['vbul'], g['sbdisk'], g['sbbul']
        )
        chi2_list.append(res['chi2_red'])
    
    print(f"Evaluated all {len(chi2_list)} galaxies with zero free parameters:")
    print(f"  Median reduced chi^2: {np.median(chi2_list):.2f}")
    print(f"  Mean reduced chi^2:   {np.mean(chi2_list):.2f}")
