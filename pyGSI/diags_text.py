"""
Code for reading text-based GSI diag files

Loosely based on https://github.com/ShawnMurdzek-NOAA/pyDA_utils/blob/main/gsi_fcts.py

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Import Modules
#---------------------------------------------------------------------------------------------------

import pandas as pd


#---------------------------------------------------------------------------------------------------
# Functions
#---------------------------------------------------------------------------------------------------

def read_text_diag(fname, ob_class='t'):
    """
    Read a text-based GSI diag files and save into a DataFrame

    Parameters
    ----------
    fname : string
        GSI diag file name
    ob_class : string
        Observation class to read (e.g., 't', 'q', 'uv')

    Returns
    -------
    df : pd.DataFrame
        GSI diag output in DataFrame format

    """

    cols = ['Observation_Class', 'null1', 'Station_ID', 'null2', 'Observation_Type', 'time', 
            'latitude', 'longitude', 'Pressure', 'Height', 'Analysis_Use_Flag', 
            'tmp0', 'tmp1', 'tmp2', 'tmp3', 'tmp4', 'tmp5']

    df = pd.read_csv(f, sep='\s+', names=cols)
    df.drop(['null1', 'null2'], axis=1, inplace=True)
    df = df.loc[df['Observation_Class'] == ob_class]
    df.reset_index(drop=True, inplace=True)

    # Extract obs, O-F, and err
    if ob_class == 'uv':
        df['u_observation'] = df['tmp0']
        df['u_omf_adjusted'] = df['tmp1']
        df['v_observation'] = df['tmp2']
        df['v_omf_adjusted'] = df['tmp3']
        df['err_final'] = df['tmp4']
        df['iusev'] = df['tmp5']
    else:
        df['observation'] = df['tmp0']
        df['omf_adjusted'] = df['tmp1']
        df['err_final'] = df['tmp2']
        df['iusev'] = df['tmp3']
    df.drop(['tmp%d' % i for i in range(6)], axis=1, inplace=True)
    
    # Compute inverse obs error
    df['errinv_final'] = np.zeros(len(df))
    df['errinv_final'][df['err_final'] > 0] = 1. / df['err_final']

    # Set multi-dimensional index to match pyGSI output
    df['Observation_Subtype'] = np.ones(len(df)) * np.nan
    indices = ['Station_ID', 'Observation_Class', 'Observation_Type',
               'Observation_Subtype', 'Pressure', 'Height',
               'Analysis_Use_Flag']
    df.set_index(indices, inplace=True)

    return df


"""
End diags_text.py
"""
