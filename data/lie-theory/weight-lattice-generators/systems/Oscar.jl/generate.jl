using Oscar

P = weight_lattice(root_system((:A, 2), (:B, 4)))
save("data.json", gens(P))
