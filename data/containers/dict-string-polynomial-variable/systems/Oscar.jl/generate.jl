using Oscar

Qx, x = QQ[:x]
save("data.json", Dict("x" => x))
