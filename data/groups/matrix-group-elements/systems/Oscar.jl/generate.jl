using Oscar

G = general_linear_group(3, 5)
save("data.json", gen(G, 1))
