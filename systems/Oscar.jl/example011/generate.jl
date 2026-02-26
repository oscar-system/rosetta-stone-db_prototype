using Oscar

d_hedron = dodecahedron()
facets(d_hedron)
vertices(d_hedron)
f_vector(d_hedron)
lattice_points(d_hedron)
obj = Dict{String, Any}(
  "unprecise" => polyhedron(Polymake.common.convert_to{Float64}(Oscar.pm_object(d_hedron))),
  "precise" => d_hedron,
)

save("data.json", obj)
