use strict;
use warnings;
use application "polytope";
my $mat = new Matrix<Rational>([[12,31,24,78],[51,63,17,35],[23,99,19,34]]);
save_data($mat, "data.json");
