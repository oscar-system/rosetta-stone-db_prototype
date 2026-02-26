using Oscar

G = small_group(24, 12)
U = sylow_subgroup(G, 2)[1]
obj = gen(U, 1)

save("data.json", obj)
