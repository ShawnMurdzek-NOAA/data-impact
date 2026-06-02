
# Generate conventional-only data impact figures for production and spinup cycles
# Edit as needed

# Ensure that the proper Python environment is loaded first

begin=2022042912
end=2022050612

for i in 0 1; do
  python generate_data_impact_figures_conv_only.py \
  	${begin} \
  	${end} \
	--spinup ${i}
done
