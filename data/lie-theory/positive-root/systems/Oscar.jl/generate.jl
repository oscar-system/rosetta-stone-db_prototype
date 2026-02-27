using Oscar

R = root_system(:A, 6)
save("data.mrdi", positive_root(R, n_positive_roots(R)))
