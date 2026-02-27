using Oscar

W = weyl_group((:A, 2), (:B, 4))
save("data.mrdi", gen(W, 1) * gen(W, 3) * gen(W, 2))
