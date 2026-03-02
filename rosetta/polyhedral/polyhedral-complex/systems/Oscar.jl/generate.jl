using Oscar

IM = incidence_matrix([[1,2,3],[1,3,4]])
vr = [0 0; 1 0; 1 1; 0 1]
obj = polyhedral_complex(IM, vr)

save("data.mrdi", obj)
