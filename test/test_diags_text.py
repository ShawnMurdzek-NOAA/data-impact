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
        return diags_text.read_text_diag(fname, ob_class='t', keep_pseudo_obs=False)

    
    def test_pseudo_ob_removal(self, sample_diag_t):
        """
        Assert that all pseudo obs have been removed
        """

        subtypes = []
        for i in range(len(sample_diag_t)):
            s = sample_diag_t.iloc[i].name[3]
            if s not in subtypes:
                subtypes.append(s)
        subtypes = np.array(subtypes)

        assert len(subtypes) == 1
        assert subtypes[0] == 0 


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
        assert row.name[0] == 'KNSI'
        assert np.isclose(row['observation'], 283.155)
        assert np.isclose(row['omf_adjusted'], 0.062625)
        assert np.isclose(row['err_final'], 1.12925)


class TestDiagUV():

    @pytest.fixture(scope='class')
    def sample_diag_uv(self):
        fname = './data/diag_results_2022020512_gsiprd.conv_ges'
        return diags_text.read_text_diag(fname, ob_class='uv', keep_pseudo_obs=False)

    
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
        assert row.name[0] == 'KNSI'
        assert np.isclose(row['u_observation'], -1.40)
        assert np.isclose(row['u_omf_adjusted'], 1.41954)
        assert np.isclose(row['v_observation'], -2.20)
        assert np.isclose(row['v_omf_adjusted'], -0.29562)
        assert np.isclose(row['err_final'], 1.6401)


"""
End test_diags_text.py 
"""
