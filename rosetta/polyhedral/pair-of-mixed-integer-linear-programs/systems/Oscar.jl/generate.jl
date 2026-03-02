using Oscar

P = dodecahedron()
F = coefficient_field(P)
a = gen(number_field(F))
MILP1 = mixed_integer_linear_program(P, [3, -2, a]; k=2, convention=:min, integer_variables=[1, 2])
MILP2 = mixed_integer_linear_program(P, [-3 * a, -2, 3]; k=2, convention=:max, integer_variables=[1, 2])
obj = [MILP1, MILP2]

save("data.mrdi", obj)
