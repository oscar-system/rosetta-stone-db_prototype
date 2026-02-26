using Oscar

G = symmetric_group(5)
obj = gen(G, 1)

save("data.json", obj)
