using Oscar

P = cube(3)
obj = mixed_integer_linear_program(P, [3, -2, 4]; k=2, convention=:min, integer_variables=[1, 2])

save("data.json", obj)
