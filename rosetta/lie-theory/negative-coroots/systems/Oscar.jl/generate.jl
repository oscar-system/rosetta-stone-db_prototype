using Oscar

R = root_system(:A, 6)
save("data.mrdi", negative_coroots(R))
