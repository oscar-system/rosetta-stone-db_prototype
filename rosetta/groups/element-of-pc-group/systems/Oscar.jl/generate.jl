using Oscar

G = small_group(24, 12)
obj = gen(G, 1)

save("data.mrdi", obj)
