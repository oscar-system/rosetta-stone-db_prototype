using Oscar

obj = phylogenetic_tree(Float64, "((H:3,(C:1,B:1):2):1,G:4);")

save("data.json", obj)
