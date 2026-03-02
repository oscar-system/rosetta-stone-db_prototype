using Oscar

W = weyl_group((:A, 2), (:B, 4))
save("data.mrdi", gens(W))
