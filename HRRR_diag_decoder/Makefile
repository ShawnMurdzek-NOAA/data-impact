# Compiler settings
FC=ifx
FFLAGS=-fp-model strict -convert big_endian -traceback

# Components of program
SRC=kinds.f90 \
    read_diag_conv.f90
OBJ=${SRC:.f90=.o}

# Compile individual f90 files
%.o: %.f90
	$(FC) $(FFLAGS) -o $@ -c $<

# Linking to create final exe
read_diag_conv.x: $(OBJ)
	$(FC) $(FFLAGS) -o $@ $(OBJ)

clean:
	rm -f *.o *.mod read_diag_conv.x 
