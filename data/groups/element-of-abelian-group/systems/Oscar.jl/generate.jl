using Oscar

A = free_abelian_group(2)
save("data.json", gen(A, 1))
