#!/bin/sh

#SBATCH --partition=hercules
#SBATCH -n 1
#SBATCH -t 1:00:00
#SBATCH -A wrfruc

# Shell script to run GSI diag decoder on a WRF_FCST_OSSE simulation

# === User configuration ===
machine='hercules'
sim_path='/work/noaa/wrfruc/murdzek/HRRR_OSSE/syn_data_WRF_FCST_OSSE_hercules/winter'
start_time=2022020100
end_time=2022020800
out_path='./diag_text_out'


# === Run GSI diag decoder ===

# Load environment
module use ./HRRR_diag_decoder/modulefiles
module load gsiutils_${machine}.intel
module list
echo

# Setup
home=`pwd`
mkdir -p ${out_path}
cd ${out_path}
cp ${home}/HRRR_diag_decoder/read_diag_conv.x .

types=( 'ges' 'anl' )
subdir=( 'gsiprd' 'gsiprd_spinup' )

# Loop over all times
current=${start_time}
while [ ${current} -le ${end_time} ]; do

echo
echo "==================="
echo "Decoding ${current}"

for s in ${subdir[@]}; do
path=${sim_path}/WRF_FCST_OSSE/run/${current}/${s}
if [[ -d ${path} ]]; then
echo ${path}
for t in ${types[@]}; do

cat << EOF > namelist.conv
&iosetup
  infilename='${path}/diag_conv_${t}.${current}',
  outfilename='diag_results_${current}_${s}.conv_${t}',
  l_obsprvdiag=.false.,
  dump_pseudo_obs_too=.true.,
 /
EOF

./read_diag_conv.x > stdout_${current}_${t}_${s}

done
fi
done

current=`date '+%Y%m%d%H' --date="${current::8} ${current:8:2} 1 hours"`

done
