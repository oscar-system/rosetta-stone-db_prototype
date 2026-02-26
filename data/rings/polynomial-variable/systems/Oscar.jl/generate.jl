using Oscar

Qx, x = QQ[:x]
save("data.json", 7*x^2 - x + 10)
