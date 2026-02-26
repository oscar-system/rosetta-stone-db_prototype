using Oscar

n2 = (QQBarField()(5))^(QQ(4//5))
obj = cube(QQBarField(), 3, -1, n2)
f_vector(obj)
lattice_points(obj)

save("data.json", obj)
