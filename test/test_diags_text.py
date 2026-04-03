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
import numpy as np

# We need to play some games to open the diags_text module...
mod_loc = '../pyGSI/diags_text.py'
mod_name = 'diags_text'
spec = importlib.util.spec_from_file_location(mod_name, mod_loc)
diags_text = importlib.util.module_from_spec(spec)
sys.modules['diags_text'] = diags_text
spec.loader.exec_module(diags_text)


#---------------------------------------------------------------------------------------------------
# Tests
#---------------------------------------------------------------------------------------------------

class TestDiagT():

    @pytest.fixture(scope='class')
    def sample_diag_t(self):
        fname = './data/diag_results_2022020512_gsiprd.conv_ges'
        return diags_text.read_text_diag(fname, ob_class='t')

    
    def test_df_len(self, sample_diag_t):
        """
        Check DataFrame length
        """

        assert len(sample_diag_t) == 15


    def test_col_names(self, sample_diag_t):
        """
        Check that column names are correct
        """

        wrong_cols = [f"tmp{n}" for n in range(6)] + ['u_observation', 'u_omf_adjusted']
        right_cols = ['observation', 'omf_adjusted', 'err_final', 'iusev']

        cols = sample_diag_t.columns
        for c in cols:
            assert c not in wrong_cols
        for c in right_cols:
            assert c in cols


    def test_sample_row(self, sample_diag_t):
        """
        Do a spot check for a single row
        """

        row = sample_diag_t.iloc[0]
        assert row.name[0] == 'KSBA'
        assert np.isclose(row['observation'], 275.94)
        assert np.isclose(row['omf_adjusted'], -7.39)
        assert np.isclose(row['err_final'], 1.1293)


class TestDiagUV():

    @pytest.fixture(scope='class')
    def sample_diag_uv(self):
        fname = './data/diag_results_2022020512_gsiprd.conv_ges'
        return diags_text.read_text_diag(fname, ob_class='uv')

    
    def test_df_len(self, sample_diag_uv):
        """
        Check DataFrame length
        """

        assert len(sample_diag_uv) == 15


    def test_col_names(self, sample_diag_uv):
        """
        Check that column names are correct
        """

        wrong_cols = [f"tmp{n}" for n in range(6)] + ['observation', 'omf_adjusted']
        right_cols = ['u_observation', 'u_omf_adjusted', 'v_observation', 'v_omf_adjusted', 
                      'err_final', 'iusev']

        cols = sample_diag_uv.columns
        for c in cols:
            assert c not in wrong_cols
        for c in right_cols:
            assert c in cols


    def test_sample_row(self, sample_diag_uv):
        """
        Do a spot check for a single row
        """

        row = sample_diag_uv.iloc[0]
        assert row.name[0] == 'KSBA'
        assert np.isclose(row['u_observation'], 0)
        assert np.isclose(row['u_omf_adjusted'], -0.06)
        assert np.isclose(row['v_observation'], 0)
        assert np.isclose(row['v_omf_adjusted'], 0.46)
        assert np.isclose(row['err_final'], 1.6503)


"""
End test_diags_text.py 
"""
