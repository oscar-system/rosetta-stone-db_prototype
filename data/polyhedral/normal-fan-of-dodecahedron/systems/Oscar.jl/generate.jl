using Oscar

obj = normal_fan(dodecahedron())
Polymake.give(Oscar.pm_object(obj), :MAXIMAL_CONES_FACETS)

save("data.mrdi", obj)
