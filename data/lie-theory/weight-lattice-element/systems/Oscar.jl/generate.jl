using Oscar

P = weight_lattice(root_system((:A, 2), (:B, 4)))
save("data.json", WeightLatticeElem(P, [1, -2, 3, 0, 2, -1]))
