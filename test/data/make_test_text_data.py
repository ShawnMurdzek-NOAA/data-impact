"""
Make test text diag files

shawn.s.murdzek@noaa.gov
"""

#---------------------------------------------------------------------------------------------------
# Input Parameters
#---------------------------------------------------------------------------------------------------

sim_dir = '../../diag_text_out'

in_fnames = [f"{sim_dir}/diag_results_2022020512_gsiprd.conv_ges",
             f"{sim_dir}/diag_results_2022020512_gsiprd.conv_anl"]
out_fnames = ['./diag_results_2022020512_gsiprd.conv_ges',
              './diag_results_2022020512_gsiprd.conv_anl']
ob_types = [120, 187, 220, 287]


#---------------------------------------------------------------------------------------------------
# Main Program
#---------------------------------------------------------------------------------------------------

for in_file, out_file in zip(in_fnames, out_fnames):
    print(in_file)

    # Save lines with desired ob types
    with open(in_file, 'r') as fptr:
        out = []
        for line in fptr:
            if int(line.split()[4]) in ob_types:
                out.append(line)

    # Write output to new file
    with open(out_file, 'w') as fptr:
        for line in out:
            fptr.write(line)


"""
End make_test_text_data.py
"""
