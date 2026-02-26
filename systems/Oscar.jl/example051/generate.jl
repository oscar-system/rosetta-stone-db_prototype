using Oscar

G = general_linear_group(3, 5)
obj = reduce(*, gens(G))

save("data.json", obj)
