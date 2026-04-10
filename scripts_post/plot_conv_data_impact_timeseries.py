#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creates time series of total data impact for each conventional observation
Reads pickle files under ./pickle and outputs figures to ./figures_post.

shawn.s.murdzek@noaa.gov
"""

import numpy as np
import matplotlib.pyplot as plt
import pickle
from pathlib import Path
import argparse
import datetime as dt
import copy
import os


# ==========================================================
#  Utilities
# ==========================================================
def read_pickle(file_path):
    """Read a pickle file and return unpacked data."""
    with open(file_path, "rb") as f:
        return pickle.load(f)


# ==========================================================
#  Time series plot
# ==========================================================
def plot_time_series(
    case_str,
    dt_list,
    alltime_sum_jo_diff,
    alltime_assim_size,
    colors,
    outdir,
    spinup,
):
    """Plot averaged-per-cycle total data impact."""
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(12, 12), constrained_layout=False)
    gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1], hspace=0.15)
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1], sharex=ax1)
    ax3 = plt.subplot(gs[2], sharex=ax1)

    for v, c in zip(alltime_sum_jo_diff.keys(), colors):
        ax1.plot(dt_list, alltime_sum_jo_diff[v], c=c, label=v)
        ax2.plot(dt_list, alltime_sum_jo_diff[v] / alltime_assim_size[v], c=c, label=v)
        ax3.plot(dt_list, alltime_assim_size[v], c=c, label=v)

    ax1.legend()

    for ax, label in zip(
        [ax1, ax2, ax3],
        ["Total Impact [Unitless]", "Impact Per Obs [Unitless]", "Assim Obs Size"],
    ):
        ax.set_ylabel(label, fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.8, color="gray")
        ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

    if spinup == 1: 
        spinup_str = '_spinup' 
    else: 
        spinup_str = ''
    fig.suptitle(f"Total Obs Impact ({case_str}{spinup_str})", fontsize=14, x=0.52, y=0.93)

    fig.savefig(outdir / f"timeseries_obs_impact{spinup_str}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ==========================================================
#  Main Function
# ==========================================================
def main(start, end, case_str, spinup=0,
         all_vars=['ps', 'pw', 't', 'q', 'uv'],
         colors=['#66CCEE', '#AA3377', '#228833', '#CCBB44', '#4477AA']):
    base_dir = Path(__file__).resolve().parents[1]
    pickle_dir = base_dir / "pickle"
    fig_dir = base_dir / "figures_post" / case_str
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Create list of datetime to iterate over
    start_dt = dt.datetime.strptime(str(start), '%Y%m%d%H')
    end_dt = dt.datetime.strptime(str(end), '%Y%m%d%H')
    dt_list = []
    current_dt = copy.deepcopy(start_dt)
    while current_dt <= end_dt:
        dt_list.append(current_dt)
        current_dt += dt.timedelta(hours=1)
    ntime = len(dt_list)

    # Accumulators for total plot
    alltime_sum_jo_diff = {}
    alltime_assim_size = {}
    for v in all_vars:
        alltime_sum_jo_diff[v] = np.zeros(ntime) * np.nan
        alltime_assim_size[v] = np.zeros(ntime) * np.nan

    # Main loop over each datetime
    for i, t in enumerate(dt_list):
        t_str = t.strftime('%Y%m%d%H')
        print(f"\nCurrent time = {t_str}")
        datapath = "." if case_str == "full-domain" else "."
        date_dir = pickle_dir / datapath

        # Loop over each variable
        sensor_type = []
        sum_jo_diff = []
        mean_jo_diff = []
        assim_size = []
        all_colors = []
        for v, c in zip(all_vars, colors):
            spinup_str = '_spinup' if spinup == 1 else ''
            sensor_str = 'conv_uv' if v == 'uv' else 'conv'
            pkl_file = date_dir / f"{t_str}_{sensor_str}{spinup_str}.pkl"

            if not pkl_file.exists():
                print(f"[WARN] Missing file for {v} at {t_str}. Skipping.")
                continue

            pkl_out = read_pickle(pkl_file)
            sensors = np.array(pkl_out[0])
            if len(sensors) == 0:
                print(f"[WARN] File for {v} at {t_str} is empty. Skipping.")
                continue

            if v not in sensors:
                print(f"[WARN] {v} is not in {pkl_file}. Skipping.")
                continue

            # Extract data from pickle file
            idx = np.where(sensors == v)[0][0]
            if pkl_out[2][idx] > 0:
                alltime_sum_jo_diff[v][i] = pkl_out[4][idx]
                alltime_assim_size[v][i] = pkl_out[2][idx]

    # -------- Final time series --------
    plot_time_series(
        case_str,
        dt_list,
        alltime_sum_jo_diff,
        alltime_assim_size,
        colors,
        fig_dir,
        spinup,
    )

    print(f"--> Figures saved to {fig_dir}")


# ==========================================================
#  CLI
# ==========================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate time series of total obs impact from pickle data.")
    parser.add_argument("start_datetime",
                        type=int,
                        help="Starting datetime in YYYYMMDDHH format")
    parser.add_argument("end_datetime",
                        type=int,
                        help="Ending datetime in YYYYMMDDHH format")
    parser.add_argument("--case", choices=["full-domain", "sub-domain"], default="full-domain",
                        help="Case to process")
    parser.add_argument("--spinup", choices=[0, 1], default=0,
                        type=int,
                        help="Which cycles to plot: 0 = production cycles, 1 = spinup cycles")
    args = parser.parse_args()

    main(args.start_datetime, args.end_datetime, args.case, spinup=args.spinup)
