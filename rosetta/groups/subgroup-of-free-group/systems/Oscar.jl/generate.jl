using Oscar

F = free_group(2)
obj = sub(F, [gen(F, 1)])[1]

save("data.mrdi", obj)
