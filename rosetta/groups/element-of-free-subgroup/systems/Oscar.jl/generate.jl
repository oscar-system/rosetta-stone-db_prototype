using Oscar

F = free_group(2)
U = sub(F, [gen(F, 1)])[1]
obj = gen(U, 1)

save("data.mrdi", obj)
