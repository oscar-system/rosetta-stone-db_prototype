#!/usr/bin/env julia
using Oscar

const ROOT = normpath(joinpath(@__DIR__, ".."))
const DESC_DIR = joinpath(ROOT, "example_descriptions")
const OSCAR_DIR = joinpath(ROOT, "systems", "Oscar.jl")

function description_md(title::String, body::String)
    return "---\ntitle: $(title)\n---\n\n# $(title)\n\n$(body)\n"
end

struct ExampleSpec
    number::Int
    title::String
    body::String
    code::String
end

examples = ExampleSpec[
    ExampleSpec(5, "Fano matroid", "Construct the Fano matroid.", """
obj = fano_matroid()
"""),
    ExampleSpec(6, "Uniform matroid", "Construct the uniform matroid U_{2,4}.", """
obj = uniform_matroid(2, 4)
"""),
    ExampleSpec(7, "Positive hull cone", "Construct a cone from two rays in QQ^2.", """
obj = positive_hull([1 0; 0 1])
"""),
    ExampleSpec(8, "Number-field cone", "Construct a cone over an embedded number field.", """
Qx, x = QQ[:x]
F, a = embedded_number_field(x^2 - 2, -1.0)
obj = positive_hull(F, [F(1) F(0); F(0) F(1)])
"""),
    ExampleSpec(9, "Square polyhedron", "Construct the square polyhedron as `cube(2)`.", """
obj = cube(2)
f_vector(obj)
"""),
    ExampleSpec(10, "Algebraic cube", "Construct a cube over `QQBarField()` with algebraic bounds.", """
n2 = (QQBarField()(5))^(QQ(4//5))
obj = cube(QQBarField(), 3, -1, n2)
f_vector(obj)
lattice_points(obj)
"""),
    ExampleSpec(11, "Dodecahedron dictionary", "Store both precise and unprecise dodecahedron polyhedra in a dictionary.", """
d_hedron = dodecahedron()
facets(d_hedron)
vertices(d_hedron)
f_vector(d_hedron)
lattice_points(d_hedron)
obj = Dict{String, Any}(
  "unprecise" => polyhedron(Polymake.common.convert_to{Float64}(Oscar.pm_object(d_hedron))),
  "precise" => d_hedron,
)
"""),
    ExampleSpec(12, "Polyhedral complex", "Construct a polyhedral complex from an incidence matrix and rational vertices.", """
IM = incidence_matrix([[1,2,3],[1,3,4]])
vr = [0 0; 1 0; 1 1; 0 1]
obj = polyhedral_complex(IM, vr)
"""),
    ExampleSpec(13, "Number-field polyhedral complex", "Construct a polyhedral complex over an embedded number field.", """
Qx, x = QQ[:x]
F, a = embedded_number_field(x^2 - 2, -1.0)
IM = incidence_matrix([[1,2,3],[1,3,4]])
vr_F = F.([0 0; 1 0; 1 1; 0 1])
obj = polyhedral_complex(IM, vr_F)
"""),
    ExampleSpec(14, "Normal fan of square", "Construct the normal fan of a square.", """
obj = normal_fan(cube(2))
"""),
    ExampleSpec(15, "Normal fan of dodecahedron", "Construct the normal fan of a dodecahedron and compute maximal-cone facets.", """
obj = normal_fan(dodecahedron())
Polymake.give(Oscar.pm_object(obj), :MAXIMAL_CONES_FACETS)
"""),
    ExampleSpec(16, "Linear program", "Construct a linear program on the cube in dimension 3.", """
P = cube(3)
obj = linear_program(P, [3, -2, 4]; k=2, convention=:min)
"""),
    ExampleSpec(17, "Pair of linear programs", "Construct two linear programs over a number field and store them as a list.", """
P = dodecahedron()
F = coefficient_field(P)
a = gen(number_field(F))
LP1 = linear_program(P, F.([3, -2, 4]); k=2, convention=:min)
LP2 = linear_program(P, F.([-1, a - 2, a + 5]); k=2, convention=:min)
ov1 = optimal_value(LP1)
ov2 = optimal_value(LP2)
obj = [LP1, LP2]
"""),
    ExampleSpec(18, "Mixed-integer linear program", "Construct a mixed-integer linear program on the cube with two integer variables.", """
P = cube(3)
obj = mixed_integer_linear_program(P, [3, -2, 4]; k=2, convention=:min, integer_variables=[1, 2])
"""),
    ExampleSpec(19, "Pair of mixed-integer linear programs", "Construct two mixed-integer linear programs over a number field.", """
P = dodecahedron()
F = coefficient_field(P)
a = gen(number_field(F))
MILP1 = mixed_integer_linear_program(P, [3, -2, a]; k=2, convention=:min, integer_variables=[1, 2])
MILP2 = mixed_integer_linear_program(P, [-3 * a, -2, 3]; k=2, convention=:max, integer_variables=[1, 2])
obj = [MILP1, MILP2]
"""),
    ExampleSpec(20, "Subdivision of points", "Construct a subdivision of points over the rationals.", """
moaepts = [4 0 0; 0 4 0; 0 0 4; 2 1 1; 1 2 1; 1 1 2]
moaeimnonreg0 = incidence_matrix([[4,5,6],[1,4,2],[2,4,5],[2,3,5],[3,5,6],[1,3,6],[1,4,6]])
obj = subdivision_of_points(moaepts, moaeimnonreg0)
"""),
    ExampleSpec(21, "Number-field subdivision", "Construct a subdivision of points over an embedded number field.", """
Qx, x = QQ[:x]
F, a = embedded_number_field(x^2 - 2, -1.0)
moaepts = [4 0 0; 0 4 0; 0 0 4; 2 1 1; 1 2 1; 1 1 2]
moaeimnonreg0 = incidence_matrix([[4,5,6],[1,4,2],[2,4,5],[2,3,5],[3,5,6],[1,3,6],[1,4,6]])
obj = subdivision_of_points(F, F.(moaepts), moaeimnonreg0)
"""),
    ExampleSpec(22, "Complex projective plane", "Construct the simplicial complex of the complex projective plane.", """
obj = complex_projective_plane()
"""),
    ExampleSpec(23, "Phylogenetic tree (Float64)", "Construct a phylogenetic tree with floating branch lengths.", """
obj = phylogenetic_tree(Float64, "((H:3,(C:1,B:1):2):1,G:4);")
"""),
    ExampleSpec(24, "Phylogenetic tree (QQ)", "Construct a phylogenetic tree with rational branch lengths.", """
obj = phylogenetic_tree(QQFieldElem, "((H:3,(C:1,B:1):2):1,G:4);")
"""),
]

function write_example_files(spec::ExampleSpec)
    exname = "example" * lpad(spec.number, 3, '0')
    desc_path = joinpath(DESC_DIR, exname * ".md")
    sys_path = joinpath(OSCAR_DIR, exname)
    mkpath(sys_path)

    write(desc_path, description_md(spec.title, spec.body))

    generate_path = joinpath(sys_path, "generate.jl")
    generate_code = "using Oscar\n\n" * strip(spec.code) * "\n\nsave(\"data.json\", obj)\n"
    write(generate_path, generate_code)

    return exname, sys_path
end

function build_object(code::String)
    expr = Meta.parse("begin\n" * code * "\nobj\nend")
    return Core.eval(Main, expr)
end

for spec in examples
    exname, sys_path = write_example_files(spec)
    obj = build_object(spec.code)
    save(joinpath(sys_path, "data.json"), obj)
    println("Generated ", exname)
end
