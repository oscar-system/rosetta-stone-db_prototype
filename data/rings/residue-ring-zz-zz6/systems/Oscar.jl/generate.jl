using Oscar

R = residue_ring(ZZ, ZZ(6))[1]
save("data.json", R(1))
