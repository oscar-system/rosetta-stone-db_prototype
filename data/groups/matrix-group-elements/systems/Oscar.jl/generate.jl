using Oscar

G = general_linear_group(3, 5)
mats = [[0 -1 0; 1 -1 0; 0 0 1], [0 1 0; 1 0 0; 0 0 1]]
matelms = map(m -> matrix(GF(5), m), mats)
obj = map(m -> G(m), matelms)

save("data.json", obj)
