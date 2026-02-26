using Oscar

Qx, x = QQ[:x]
F, a = embedded_number_field(x^2 - 2, -1.0)
moaepts = [4 0 0; 0 4 0; 0 0 4; 2 1 1; 1 2 1; 1 1 2]
moaeimnonreg0 = incidence_matrix([[4,5,6],[1,4,2],[2,4,5],[2,3,5],[3,5,6],[1,3,6],[1,4,6]])
obj = subdivision_of_points(F, F.(moaepts), moaeimnonreg0)

save("data.json", obj)
