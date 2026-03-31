# HRRR-era GSI Diag Decoder

This Fortran is a modification of `GSI-utils/src/Analysis_Utilities/read_diag` with additional output fields needed for the Todling (2013) obs space data impact metric.

## Building

```
module use modulefiles
module load gsiutils_<machine>.intel
make
```

## Running

### Namelist options

All namelist options ar ein a single section titled `&iosetup`.

| Parameter | Default | Description |
| --------- | ------- | ----------- |
| `infilename` | diag\_conv.dat | Input GSI diag binary file name. |
| `outfilename` | diag\_results | Output file with GSI diag file information in a table. |
| `l_obsprvdiag` | .false. | Option to output observation provider information (currently does not work). |
| `dump_pseudo_obs_too` | .false. | Option to also dump pseudo observations. |
