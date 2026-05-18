#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modernized Data Impact Plotter for Conventional Obs ONLY

Two subplots are created per figure: 
    1. Number of obs assimilated in first experiments
    2. Impact per ob for the first provided experiment 
    3. Differences in impact per ob between the first and second experiment
    4. Percent differences in impact per ob between the first and second experiment

Only total (summed, not averaged) plots are created

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
#  Total (Averaged) Plot
# ==========================================================
def plot_total_summary(
    case_str,
    ncyc,
    all_sensor_type,
    alltime_sum_jo_diff,
    alltime_assim_size,
    colors,
    spinup,
    sim1,
    sim2,
    tag=''
):
    """Plot total data impact."""
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(20, 8), constrained_layout=False)
    gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 1], wspace=0.10)
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1], sharey=ax1)
    ax3 = plt.subplot(gs[2], sharey=ax1)
    ax4 = plt.subplot(gs[3], sharey=ax1)

    # Compute percent differences
    diff = []
    pct_diff = []
    idx_sim1 = []
    for i, s in enumerate(all_sensor_type[sim1]):
        try:
            i_sim2 = np.where(all_sensor_type[sim2] == s)[0][0]
        except:
            print(f"{s} is missing from sim2")
            continue

        idx_sim1.append(i)
        sim1_impact_per_ob = alltime_sum_jo_diff[sim1][i] / alltime_assim_size[sim1][i]
        sim2_impact_per_ob = alltime_sum_jo_diff[sim2][i_sim2] / alltime_assim_size[sim2][i_sim2]
        diff.append(sim2_impact_per_ob - sim1_impact_per_ob)
        pct_diff.append(100*diff[-1] / sim1_impact_per_ob)


    ax1.barh(range(len(all_sensor_type[sim1][idx_sim1])), 
             alltime_assim_size[sim1][idx_sim1], 
             color=colors[sim1][idx_sim1])
    ax2.barh(range(len(all_sensor_type[sim1][idx_sim1])), 
             alltime_sum_jo_diff[sim1][idx_sim1] / alltime_assim_size[sim1][idx_sim1], 
             color=colors[sim1][idx_sim1])
    ax3.barh(range(len(all_sensor_type[sim1][idx_sim1])), 
             diff, 
             color=colors[sim1][idx_sim1])
    ax4.barh(range(len(all_sensor_type[sim1][idx_sim1])), 
             pct_diff, 
             color=colors[sim1][idx_sim1])

    for ax, label in zip(
        [ax1, ax2, ax3, ax4],
        ["Total Assim Obs for Sim1", "Sim1 Impact Per Obs [Unitless]", "Impact Per Ob Diff [Unitless]", "Impact Per Ob % Diff"],
    ):
        ax.set_xlabel(label, fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.8, color="gray")
        ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    
    ax1.invert_yaxis()
    ax1.set_yticks(range(len(all_sensor_type[sim1][idx_sim1])))
    ax1.set_yticklabels(all_sensor_type[sim1][idx_sim1], fontsize=10)
    plt.setp(ax2.get_yticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), visible=False)
    plt.setp(ax4.get_yticklabels(), visible=False)

    if spinup == 1: 
        spinup_str = 'spinup' 
    else: 
        spinup_str = 'prod'
    fig.suptitle(f"{tag} Total Impact ({spinup_str}). Sim1 cycles = {ncyc[sim1]}, Sim2 cycles = {ncyc[sim2]}. Diffs are Sim2 $-$ Sim1", fontsize=14, x=0.52, y=0.93)

    fig.savefig(f"impact_pct_diff_{spinup_str}_{tag}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ==========================================================
#  Main Function
# ==========================================================
def main(sim1, sim2, start, end, case_str, spinup=0, tag='',
         all_vars=['ps', 'pw', 't', 'q', 'uv'],
         colors=['#66CCEE', '#AA3377', '#228833', '#CCBB44', '#4477AA']):

    # Create list of datetime to iterate over
    start_dt = dt.datetime.strptime(str(start), '%Y%m%d%H')
    end_dt = dt.datetime.strptime(str(end), '%Y%m%d%H')
    dt_list = []
    current_dt = copy.deepcopy(start_dt)
    while current_dt <= end_dt:
        dt_list.append(current_dt)
        current_dt += dt.timedelta(hours=1)

    # Accumulators for total plot
    alltime_sensor_type = {}
    alltime_sum_jo_diff = {}
    alltime_assim_size = {}
    alltime_colors = {}
    ncyc = {}

    for sim in [sim1, sim2]:
 
        print(f"\n\n{sim}\n")

        # Accumulators for total plot
        alltime_sensor_type[sim] = []
        alltime_sum_jo_diff[sim] = []
        alltime_assim_size[sim] = []
        alltime_colors[sim] = []
        ncyc[sim] = 0

        # Main loop over each datetime
        for t in dt_list:
            t_str = t.strftime('%Y%m%d%H')
            print(f"\nCurrent time = {t_str}")
            datapath = "." if case_str == "full-domain" else "."
            date_dir = f"{sim}/{datapath}"

            # Loop over each variable
            sensor_type = []
            sum_jo_diff = []
            mean_jo_diff = []
            assim_size = []
            all_colors = []
            for v, c in zip(all_vars, colors):
                if spinup == 1:
                    pkl_file = f"{date_dir}/{t_str}_conv_{v}_spinup_detail.pkl"
                else:
                    pkl_file = f"{date_dir}/{t_str}_conv_{v}_detail.pkl"

                if not os.path.isfile(pkl_file):
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

                # -------- Accumulate totals --------
                ncyc[sim] += 1
                for j, s in enumerate(sensor_type):
                    if s in alltime_sensor_type[sim]:
                        idx = alltime_sensor_type[sim].index(s)
                        alltime_sum_jo_diff[sim][idx] = alltime_sum_jo_diff[sim][idx] + sum_jo_diff[j]
                        alltime_assim_size[sim][idx] = alltime_assim_size[sim][idx] + assim_size[j]
                    else:
                        alltime_sensor_type[sim].append(s)
                        alltime_sum_jo_diff[sim].append(sum_jo_diff[j])
                        alltime_assim_size[sim].append(assim_size[j])
                        alltime_colors[sim].append(all_colors[j])

        # Convert to arrays
        alltime_sensor_type[sim] = np.array(alltime_sensor_type[sim])
        sort_idx = np.argsort(alltime_sensor_type[sim])
        alltime_sensor_type[sim] = alltime_sensor_type[sim][sort_idx]
        alltime_sum_jo_diff[sim] = np.array(alltime_sum_jo_diff[sim])[sort_idx]
        alltime_assim_size[sim] = np.array(alltime_assim_size[sim])[sort_idx]
        alltime_colors[sim] = np.array(alltime_colors[sim])[sort_idx]

    # -------- Total averaged plot --------
    plot_total_summary(
            case_str,
            ncyc,
            alltime_sensor_type,
            alltime_sum_jo_diff,
            alltime_assim_size,
            alltime_colors,
            spinup,
            sim1,
            sim2,
            tag=tag
        )

    print(f"--> Figure saved")


# ==========================================================
#  CLI
# ==========================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate FSOI proxy plots from pickle data.")
    parser.add_argument("ctrl_output",
                        type=str,
                        help="Directory containing data-impact pickle output for the control experiment")
    parser.add_argument("exp_output",
                        type=str,
                        help="Directory containing data-impact pickle output for the comparison experiment")
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
    parser.add_argument("--tag", default='',
                        type=str,
                        help="Tag to add to output file name and title")
    args = parser.parse_args()

    main(args.ctrl_output, args.exp_output, args.start_datetime, args.end_datetime, args.case, spinup=args.spinup, tag=args.tag)
