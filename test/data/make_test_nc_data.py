"""
Make test netCDF files

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import xarray as xr


#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

sim_dir = '/work2/noaa/wrfruc/murdzek/RRFS_OSSE/real_red_data_rrfs-workflow_orion/winter/NCO_dirs/ptmp/prod/rrfs.20220201/12'

in_fnames = [f"{sim_dir}/diag_conv_t_ges.2022020112.nc4",
             f"{sim_dir}/diag_conv_t_anl.2022020112.nc4",
             f"{sim_dir}/diag_conv_uv_ges.2022020112.nc4",
             f"{sim_dir}/diag_conv_uv_anl.2022020112.nc4"]
out_fnames = ['./diag_conv_t_ges.2022020112.nc4',
              './diag_conv_t_anl.2022020112.nc4',
              './diag_conv_uv_ges.2022020112.nc4',
              './diag_conv_uv_anl.2022020112.nc4']
ob_types = [120, 187, 220, 287]


#---------------------------------------------------------------------------------------------------
# Main Program
#---------------------------------------------------------------------------------------------------

for in_file, out_file in zip(in_fnames, out_fnames):
    print(in_file)
    ds = xr.open_dataset(in_file)
    ds = ds.where(ds['Observation_Type'].isin(ob_types), drop=True)
    ds.to_netcdf(out_file)
    ds.close()


"""
End make_test_nc_data.py
"""
