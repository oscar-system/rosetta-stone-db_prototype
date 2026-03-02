using Oscar

Qx, x = QQ[:x]
save("data.mrdi", Dict("x" => x))
