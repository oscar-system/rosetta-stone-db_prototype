using Oscar

F = free_group(2)
x1 = gen(F, 1)
x2 = gen(F, 2)
G = quo(F, [x1^2, x2^2, comm(x1, x2)])[1]
obj = sub(G, [gen(G, 1)])[1]

save("data.json", obj)
