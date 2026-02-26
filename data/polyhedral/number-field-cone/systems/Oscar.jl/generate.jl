using Oscar

Qx, x = QQ[:x]
F, a = embedded_number_field(x^2 - 2, -1.0)
obj = positive_hull(F, [F(1) F(0); F(0) F(1)])

save("data.json", obj)
