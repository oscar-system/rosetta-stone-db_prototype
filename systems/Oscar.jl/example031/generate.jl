using Oscar

F = free_group(2)
obj = gen(F, 1)

save("data.json", obj)
