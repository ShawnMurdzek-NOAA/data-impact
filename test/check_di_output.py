"""
Check output from data-impact for test data

shawn.s.murdzek@noaa.gov
"""

"""
Tests for pyGSI/diags_text.py

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import pytest
import importlib
import sys
import os
import numpy as np
import pickle
import datetime as dt
import xarray as xr

# We need to play some games to open the diags_text module...
mod_loc = 'pyGSI/diags_text.py'
mod_name = 'diags_text'
spec = importlib.util.spec_from_file_location(mod_name, mod_loc)
diags_text = importlib.util.module_from_spec(spec)
sys.modules['diags_text'] = diags_text
spec.loader.exec_module(diags_text)


#---------------------------------------------------------------------------------------------------
# Tests
#---------------------------------------------------------------------------------------------------

def check_out_files_exist(path, time, variables=['t', 'uv']):
    """
    Check that all expected output files exist
    """

    t_str = time.strftime('%Y%m%d%H')

    files = []
    for v in variables:
        files.append(f"{path}/figures/{v}-{t_str}.png")
        files.append(f"{path}/pickle_detail/{t_str}_conv_{v}_detail.pkl")
    if (len(variables) > 1) or (len(variables) == 1 and 'uv' not in variables):
        files.append(f"{path}/pickle/{t_str}_conv.pkl")
    if 'uv' in variables:
        files.append(f"{path}/pickle/{t_str}_conv_uv.pkl")

    err = 0
    for f in files:
        if not os.path.exists(f):
            print(f"[ERROR] Missing {f}")
            err = 1

    return err


def check_pickle_detail(path, time, var='t', ftype='netcdf'):
    """
    Check various aspects of a pickle_detail file
    """

    pkl_fname = f"{path}/pickle_detail/{time.strftime('%Y%m%d%H')}_conv_{var}_detail.pkl"
    with open(pkl_fname, 'rb') as f:
        pkl_out = pickle.load(f)

    err = 0

    if ftype == 'netcdf':

        diag = {}
        for typ in ['ges', 'anl']:
            fname = f"{path}/test/data/{time.strftime('%H')}/diag_conv_{var}_{typ}.{time.strftime('%Y%m%d%H')}.nc4"
            diag[typ] = xr.open_dataset(fname)

        n = np.sum(diag['ges']['Analysis_Use_Flag'] == 1)
        if var == 'uv':
            n = 2*n
        if len(pkl_out['jo_diff']) != n:
            print(f"[ERROR] Mismatch between size of pickle_detail and raw diag file")
            err = 1
         
        idx = np.where(diag['ges']['Analysis_Use_Flag'] == 1)[0][0]
        omf = 'Obs_Minus_Forecast_adjusted'
        if var == 'uv':
            omf = 'u_Obs_Minus_Forecast_adjusted'
        metric = (diag['anl'][omf].values[idx]**2 - diag['ges'][omf].values[idx]**2) * diag['anl']['Errinv_Final'].values[idx]**2
        if not np.isclose(pkl_out['jo_diff'][0], metric):
            print(f"[ERROR] Computed jo_diff is incorrect")
            err = 1

    elif ftype == 'text':

        diag = {}
        for typ in ['ges', 'anl']:
            fname = f"{path}/test/data/diag_results_{time.strftime('%Y%m%d%H')}_gsiprd.conv_{typ}"
            diag[typ] = diags_text.read_text_diag(fname, ob_class=var)

        n = 0
        idx = np.nan
        for i in range(len(diag['ges'])):
            n = n + (diag['ges'].iloc[i].name[6] == 1)
            if np.isnan(idx): idx = i
        if var == 'uv':
            n = 2*n
        if len(pkl_out['jo_diff']) != n:
            print(f"[ERROR] Mismatch between size of pickle_detail and raw diag file")
            err = 1
         
        omf = 'omf_adjusted'
        if var == 'uv':
            omf = 'u_omf_adjusted'
        metric = (diag['anl'][omf].values[idx]**2 - diag['ges'][omf].values[idx]**2) * diag['anl']['errinv_final'].values[idx]**2
        if not np.isclose(pkl_out['jo_diff'][0], metric):
            print(f"[ERROR] Computed jo_diff is incorrect {metric} {pkl_out['jo_diff'][0]}")
            err = 1

    return err


if __name__ == '__main__':

    path = sys.argv[1]
    time = dt.datetime.strptime(sys.argv[2], '%Y%m%d%H')
    ftype = sys.argv[3]
    variables = ['t', 'uv']

    print('\nStarting Python checks')
    err = check_out_files_exist(path, time, variables=variables)
    for v in variables:
        err = max(check_pickle_detail(path, time, var=v, ftype=ftype), err)

    print(f"\nMax error code = {err}\n")


"""
End check_di_output.py
"""
