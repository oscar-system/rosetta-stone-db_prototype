using Oscar

P = cube(3)
obj = linear_program(P, [3, -2, 4]; k=2, convention=:min)

save("data.json", obj)
