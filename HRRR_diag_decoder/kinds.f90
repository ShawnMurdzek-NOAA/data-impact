module kinds
! Stripped down version of gsi/kinds.F90 for this utility
! This is to avoid building and depending on the entire GSI compiled library
  implicit none

  public i_kind, i_byte, i_short, i_long, i_llong
  public r_kind, r_single, r_double, r_quad

  private
  integer, parameter :: default_integer = 3  ! 1=byte,
                                             ! 2=short,
                                             ! 3=long,
                                             ! 4=llong
  integer, parameter :: i_byte  = selected_int_kind(1)      ! byte  integer
  integer, parameter :: i_short = selected_int_kind(4)      ! short integer
  integer, parameter :: i_long  = selected_int_kind(8)      ! long  integer
  integer, parameter :: llong_t = selected_int_kind(16)     ! llong integer
  integer, parameter :: i_llong = max( llong_t, i_long )
   integer, parameter, dimension(4) :: integer_types = (/ &
       i_byte, i_short, i_long,  i_llong  /)
  integer, parameter :: i_kind = integer_types( default_integer )

  !integer, parameter :: default_real = 1  ! 1=single
  integer, parameter :: default_real = 2  ! 2=double
  !integer, parameter :: default_real = 3  ! 3=quad
  !integer, parameter :: default_real = 1  ! 1=single

  integer, parameter :: r_single = selected_real_kind(6)  ! single precision
  integer, parameter :: r_double = selected_real_kind(15) ! double precision
  integer, parameter :: quad_t   = selected_real_kind(20) ! quad precision
  integer, parameter :: r_quad   = max( quad_t, r_double )
  integer, parameter, dimension(3) :: &
     real_kinds = (/ r_single, r_double, r_quad /)
  integer, parameter  :: r_kind = real_kinds( default_real )
end module kinds
