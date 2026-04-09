#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modernized Data Impact Plotter for Conventional Obs ONLY
Reads pickle files under ./pickle_detail and outputs figures to ./figures_post.

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
#  Per-cycle Plot
# ==========================================================
def plot_cycle(
    datestr,
    all_sensor_type,
    all_sum_jo_diff,
    all_mean_jo_diff,
    all_assim_size,
    colors,
    outdir,
    spinup,
):
    """Plot and save one analysis cycle figure."""
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(18, 8), constrained_layout=False)
    gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 1], wspace=0.10)
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1], sharey=ax1)
    ax3 = plt.subplot(gs[2], sharey=ax1)

    # -------- Bar 1: Total Impact --------
    ax1.barh(range(len(all_sensor_type)), all_sum_jo_diff, color=colors)
    ax1.set_yticks(range(len(all_sensor_type)))
    ax1.set_yticklabels(all_sensor_type, fontsize=10)
    ax1.invert_yaxis()
    ax1.set_xlabel("Total Impact [Unitless]", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.8, color="gray")

    # -------- Bar 2: Impact per Obs --------
    ax2.barh(range(len(all_sensor_type)), all_mean_jo_diff, color=colors)
    ax2.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    ax2.set_xlabel("Impact Per Obs [Unitless]", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.8, color="gray")
    plt.setp(ax2.get_yticklabels(), visible=False)

    # -------- Bar 3: Assim Obs Size --------
    ax3.barh(range(len(all_sensor_type)), all_assim_size, color=colors)
    ax3.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    ax3.set_xlabel("Assim Obs Size", fontsize=11)
    ax3.grid(True, linestyle="--", alpha=0.8, color="gray")
    plt.setp(ax3.get_yticklabels(), visible=False)

    if spinup == 1:
        spinup_str = '_spinup' 
    else: 
        spinup_str = ''
    fig.suptitle(f"Date = {datestr}{spinup_str}", fontsize=14, x=0.52, y=0.93)

    out_path = outdir / f"{datestr}{spinup_str}-fsoi-proxy.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ==========================================================
#  Total (Averaged) Plot
# ==========================================================
def plot_total_summary(
    case_str,
    datestr_len,
    all_sensor_type,
    alltime_sum_jo_diff,
    alltime_assim_size,
    colors,
    outdir,
    spinup,
):
    """Plot averaged-per-cycle total data impact."""
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(18, 8), constrained_layout=False)
    gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 1], wspace=0.10)
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1], sharey=ax1)
    ax3 = plt.subplot(gs[2], sharey=ax1)

    ax1.barh(range(len(all_sensor_type)), alltime_sum_jo_diff / datestr_len, color=colors)
    ax2.barh(range(len(all_sensor_type)), alltime_sum_jo_diff / alltime_assim_size, color=colors)
    ax3.barh(range(len(all_sensor_type)), alltime_assim_size / datestr_len, color=colors)

    for ax, label in zip(
        [ax1, ax2, ax3],
        ["Total Impact [Unitless]", "Impact Per Obs [Unitless]", "Assim Obs Size Per Cycle"],
    ):
        ax.set_xlabel(label, fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.8, color="gray")
        ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
        ax.invert_yaxis()

    ax1.set_yticks(range(len(all_sensor_type)))
    ax1.set_yticklabels(all_sensor_type, fontsize=10)
    plt.setp(ax2.get_yticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), visible=False)

    if spinup == 1: 
        spinup_str = '_spinup' 
    else: 
        spinup_str = ''
    fig.suptitle(f"Cycle-Averaged Total Impact ({case_str}{spinup_str}). Cycles = {datestr_len}", fontsize=14, x=0.52, y=0.93)

    fig.savefig(outdir / f"total-fsoi-proxy{spinup_str}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ==========================================================
#  Main Function
# ==========================================================
def main(start, end, case_str, mode="each", spinup=0, 
         all_vars=['ps', 'pw', 't', 'q', 'uv'],
         colors=['#66CCEE', '#AA3377', '#228833', '#CCBB44', '#4477AA']):
    base_dir = Path(__file__).resolve().parents[1]
    pickle_dir = base_dir / "pickle_detail"
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

    # Accumulators for total plot
    alltime_sensor_type = []
    alltime_sum_jo_diff = []
    alltime_assim_size = []
    alltime_colors = []
    ncyc = 0

    # Main loop over each datetime
    for t in dt_list:
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
            if spinup == 1:
                pkl_file = date_dir / f"{t_str}_conv_{v}_spinup_detail.pkl"
            else:
                pkl_file = date_dir / f"{t_str}_conv_{v}_detail.pkl"

            if not pkl_file.exists():
                print(f"[WARN] Missing file for {v} at {t_str}. Skipping.")
                continue

            pkl_out = read_pickle(pkl_file)
            obs = np.unique(pkl_out['observation_type'])
            if len(obs) == 0:
                print(f"[WARN] File for {v} at {t_str} is empty. Skipping.")
                continue

            # Extract data from pickle file
            for o in obs:
                idx = np.where(pkl_out['observation_type'] == o)[0]
                sensor_type.append(f"{v}_{o}")
                sum_jo_diff.append(np.sum(pkl_out['jo_diff'][idx]))
                mean_jo_diff.append(np.mean(pkl_out['jo_diff'][idx]))
                assim_size.append(len(idx))
                all_colors.append(c)

        if len(sensor_type) == 0:
            print(f"[WARN] No pickle files found for {t_str}")
        else:

            # -------- Per-cycle plots --------
            if mode in ["each", "both"]:
                plot_cycle(
                    t_str,
                    sensor_type,
                    sum_jo_diff,
                    mean_jo_diff,
                    assim_size,
                    all_colors,
                    fig_dir,
                    spinup,
                )

            # -------- Accumulate totals --------
            ncyc += 1
            for j, s in enumerate(sensor_type):
                if s in alltime_sensor_type:
                    idx = alltime_sensor_type.index(s)
                    alltime_sum_jo_diff[idx] = alltime_sum_jo_diff[idx] + sum_jo_diff[j]
                    alltime_assim_size[idx] = alltime_assim_size[idx] + assim_size[j]
                else:
                    alltime_sensor_type.append(s)
                    alltime_sum_jo_diff.append(sum_jo_diff[j])
                    alltime_assim_size.append(assim_size[j])
                    alltime_colors.append(all_colors[j])

    # -------- Total averaged plot --------
    alltime_sensor_type = np.array(alltime_sensor_type)
    sort_idx = np.argsort(alltime_sensor_type)
    alltime_sensor_type = alltime_sensor_type[sort_idx]
    alltime_sum_jo_diff = np.array(alltime_sum_jo_diff)[sort_idx]
    alltime_assim_size = np.array(alltime_assim_size)[sort_idx]
    alltime_colors = np.array(alltime_colors)[sort_idx]
    if mode in ["total", "both"]:
        plot_total_summary(
            case_str,
            ncyc,
            alltime_sensor_type,
            alltime_sum_jo_diff,
            alltime_assim_size,
            alltime_colors,
            fig_dir,
            spinup,
        )

    print(f"--> Figures saved to {fig_dir}")


# ==========================================================
#  CLI
# ==========================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate FSOI proxy plots from pickle data.")
    parser.add_argument("start_datetime",
                        type=int,
                        help="Starting datetime in YYYYMMDDHH format")
    parser.add_argument("end_datetime",
                        type=int,
                        help="Ending datetime in YYYYMMDDHH format")
    parser.add_argument("--case", choices=["full-domain", "sub-domain"], default="full-domain",
                        help="Case to process")
    parser.add_argument("--mode", choices=["each", "total", "both"], default="both",
                        help="Plot mode: 'each' = per-cycle only, 'total' = total only, 'both' = both types")
    parser.add_argument("--spinup", choices=[0, 1], default=0,
                        type=int,
                        help="Which cycles to plot: 0 = production cycles, 1 = spinup cycles")
    args = parser.parse_args()

    main(args.start_datetime, args.end_datetime, args.case, mode=args.mode, spinup=args.spinup)
