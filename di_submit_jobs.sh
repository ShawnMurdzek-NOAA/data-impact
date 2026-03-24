#!/bin/sh --login
  
#SBATCH --partition=hercules
#SBATCH -n 1
#SBATCH -t 2:00:00
#SBATCH --mem=12g
#SBATCH -A wrfruc
#SBATCH -q batch


# Loading modules
#module use -a /scratch3/BMC/wrfruc/gge/Miniforge3/modulefiles
#module load Miniforge3/24.11.3-2
#module load pyDAmonitor/1.0.0

module purge
module use /work2/noaa/wrfruc/murdzek/conda/miniforge_hercules/modulefiles
module load miniforge3/25.3.0
conda activate base
conda activate /work2/noaa/wrfruc/murdzek/conda/miniforge_hercules/env/my_py
  
# Running scripts  
#python di_sate.py    $YEAR $MONTH $DAY $HOUR $DATAPATH "$DOMAIN" "$SAVE_DETAIL"
python di_conv.py    $YEAR $MONTH $DAY $HOUR $DATAPATH "$DOMAIN" "$SAVE_DETAIL"
python di_conv_uv.py $YEAR $MONTH $DAY $HOUR $DATAPATH "$DOMAIN" "$SAVE_DETAIL"

