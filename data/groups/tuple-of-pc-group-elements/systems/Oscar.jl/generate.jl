using Oscar

G = small_group(24, 12)
x = gen(G, 1)
U = sylow_subgroup(G, 2)[1]
y = gen(U, 1)
obj = (x, x^2, y)

save("data.json", obj)
