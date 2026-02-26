using Oscar

F = free_group(2)
x = gen(F, 1)
U = sub(F, [gen(F, 1)])[1]
y = gen(U, 1)
obj = (x, x^2, y)

save("data.json", obj)
