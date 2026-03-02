using Oscar

G = symmetric_group(5)
U = sylow_subgroup(G, 2)[1]
obj = gen(U, 1)

save("data.mrdi", obj)
