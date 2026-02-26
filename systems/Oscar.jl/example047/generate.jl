using Oscar

G = small_group(24, 12)
obj = sylow_subgroup(G, 2)[1]

save("data.json", obj)
