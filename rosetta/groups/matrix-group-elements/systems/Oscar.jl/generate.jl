using Oscar

G = general_linear_group(3, 5)
save("data.mrdi", gen(G, 1))
