using Oscar

Qx, x = QQ[:x]
save("data.mrdi", Set([x, x^2]))
