using Oscar

Qx, x = QQ[:x]
save("data.json", Set([x, x^2]))
