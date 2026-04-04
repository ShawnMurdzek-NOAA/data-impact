#!/bin/sh

# Run data-impact on a test set of conventional obs and check output using Python

# NOTE: It is assumed that you already have an appropriate Python environment loaded

mkdir -p figures logs pickle pickle_detail

# ==============================================================================
# Test text diag files

YEAR='2022'
MONTH='02'
DAY='05'
HOUR='12'
DATAPATH='./test/data'
DOMAIN='True'
SAVE_DETAIL='true'
FTYPE='text'

python di_conv.py    $YEAR $MONTH $DAY $HOUR $DATAPATH "$DOMAIN" "$SAVE_DETAIL" "$FTYPE"
python di_conv_uv.py $YEAR $MONTH $DAY $HOUR $DATAPATH "$DOMAIN" "$SAVE_DETAIL" "$FTYPE"

python test/check_di_output.py "./" "${YEAR}${MONTH}${DAY}${HOUR}" text

echo
echo


# ==============================================================================
# Test netCDF diag files

YEAR='2022'
MONTH='02'
DAY='01'
HOUR='12'
DATAPATH='./test/data'
DOMAIN='True'
SAVE_DETAIL='true'
FTYPE='netcdf'

python di_conv.py    $YEAR $MONTH $DAY $HOUR $DATAPATH "$DOMAIN" "$SAVE_DETAIL" "$FTYPE"
python di_conv_uv.py $YEAR $MONTH $DAY $HOUR $DATAPATH "$DOMAIN" "$SAVE_DETAIL" "$FTYPE"

python test/check_di_output.py "./" "${YEAR}${MONTH}${DAY}${HOUR}" netcdf
