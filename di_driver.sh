#!/bin/sh
 
# === User configuration ===
YEAR=2022
DATAPATH='./test/data'

# please comment out one of them: 1) True, for the entire domain; 2) or a prescribed rectangular sub-domain
DOMAIN_STR="True" 
#DOMAIN_STR="(anl_latitude>15) & (anl_latitude<43) & (anl_longitude>267) & (anl_longitude<282)"

# whether to save detailed pickle files ("true" to enable, anything else disables)
SAVE_DETAIL="true"
#SAVE_DETAIL="false"

# whether netcdf of text diag files are used
FTYPE='netcdf'

# === Setup output directories ===
mkdir -p figures logs pickle pickle_detail

# === Cycles to process ===
for MM in 02; do
  
  # for DD in 27 28; do
  for DD in 01; do
	  
    #for HH in {00..23}; do
    for HH in 12; do
	        
      CYCLE="${YEAR}${MM}${DD}${HH}"
	  JOBNAME="pygsi_${CYCLE}"
	  LOGFILE="logs/${JOBNAME}.log"
	  if [[ ${FTYPE} == 'netcdf' ]]; then
	    DIAG_PATH="${DATAPATH}/rrfs.${YEAR}${MM}${DD}"
	  elif [[ $FTYPE} == 'text' ]]; then
            DIAG_PATH=${DATAPATH}
	  fi

	  echo "=== Processing cycle ${CYCLE} ==="
	  echo "  - Data path: ${RRFS_PATH}"
									
	  # remove previous log if exists
	  [ -f "${LOGFILE}" ] && rm -f "${LOGFILE}"

	  # submit the job to Slurm
	  sbatch -J "${JOBNAME}" \
             -o "${LOGFILE}" \
             --export=YEAR=${YEAR},MONTH=${MM},DAY=${DD},HOUR=${HH},DATAPATH=${DIAG_PATH}/,DOMAIN="${DOMAIN_STR}",SAVE_DETAIL=${SAVE_DETAIL},FTYPE=${FTYPE} \
	         di_submit_jobs.sh					   			   			

    done
  done
done

