#!/usr/bin/env julia
using Oscar

const ROOT = normpath(joinpath(@__DIR__, ".."))
const BASE = joinpath(ROOT, "data", "rings")

R, (x, y, z) = QQ[:x, :y, :z]

items = [
  ("zz-integer", ZZ(42)),
  ("rational-number", QQ(42, 23)),
  ("prime-field-one", one(GF(5))),
  ("finite-field-generator", gen(GF(5, 2))),
  ("multivariate-polynomial", 3*x^2*y - 5*y^5*z),
]

for (slug, obj) in items
  out = joinpath(BASE, slug, "systems", "Oscar.jl", "data.json")
  mkpath(dirname(out))
  save(out, obj)
  println("Generated ", slug)
end
