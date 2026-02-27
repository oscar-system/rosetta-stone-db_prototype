using Oscar

R = root_system(:A, 6)
save("data.mrdi", positive_coroot(R, n_positive_roots(R)))
