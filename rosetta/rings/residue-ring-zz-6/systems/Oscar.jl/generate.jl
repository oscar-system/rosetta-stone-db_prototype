using Oscar

R = residue_ring(ZZ, 6)[1]
save("data.mrdi", R(1))
