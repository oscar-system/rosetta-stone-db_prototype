using Oscar

P = dodecahedron()
F = coefficient_field(P)
a = gen(number_field(F))
LP1 = linear_program(P, F.([3, -2, 4]); k=2, convention=:min)
LP2 = linear_program(P, F.([-1, a - 2, a + 5]); k=2, convention=:min)
ov1 = optimal_value(LP1)
ov2 = optimal_value(LP2)
obj = [LP1, LP2]

save("data.mrdi", obj)
