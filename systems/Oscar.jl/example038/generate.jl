using Oscar

dom = free_abelian_group(2)
codom = free_abelian_group(3)
mat = matrix(ZZ, [[1, 2, 3], [2, 3, 4]])
obj = hom(dom, codom, mat)

save("data.json", obj)
