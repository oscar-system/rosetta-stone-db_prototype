using Oscar
A = matrix(QQ,[31 24 78; 63 17 35; 99 19 34]);
b = [12, 51, 23]
P = polyhedron(-A, b)
println(vertices(P))
w = [64449, 26552, 73367]
LP = linear_program(P,w;k=0,convention = :min)
println(optimal_value(LP))
save("data.mrdi", LP)
