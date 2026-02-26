using Oscar

R = root_system(:A, 6)
save("data.json", negative_coroots(R))
