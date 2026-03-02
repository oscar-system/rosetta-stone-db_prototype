using Oscar

Qx, x = QQ[:x]
F, a = embedded_number_field(x^2 - 2, -1.0)
IM = incidence_matrix([[1,2,3],[1,3,4]])
vr_F = F.([0 0; 1 0; 1 1; 0 1])
obj = polyhedral_complex(IM, vr_F)

save("data.mrdi", obj)
