use strict;
use warnings;
use application "polytope";
my $A = new Matrix<Rational>([[31,24,78],[63,17,35],[99,19,34]]);
my $b = new Vector<Rational>([12, 51, 23]);
my $w = new Vector<Rational>([64449, 26552, 73367]);

my $P = new Polytope(INEQUALITIES=>($b|$A));
my $lp = $P->LP(LINEAR_OBJECTIVE=>zero_vector(1)|$w);

save_data($P, "data.json");
