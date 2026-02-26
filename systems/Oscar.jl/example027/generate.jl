using Oscar

G = symmetric_group(5)
obj = sylow_subgroup(G, 2)[1]

save("data.json", obj)
