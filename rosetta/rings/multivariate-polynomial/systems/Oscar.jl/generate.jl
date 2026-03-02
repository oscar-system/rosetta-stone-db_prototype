using Oscar

R, (x, y, z) = QQ[:x, :y, :z]
save("data.mrdi", 3*x^2*y - 5*y^5*z)
