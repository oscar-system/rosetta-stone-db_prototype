#!/usr/bin/env julia
using Oscar

const ROOT = normpath(joinpath(@__DIR__, ".."))
const BASE = joinpath(ROOT, "data", "basics")

items = [
  ("int", 42),
  ("bool", true),
  ("string", "string"),
  ("vector-int", Int[1, 2, 3, 4]),
  ("mixed-tuple", (1, "string", true)),
]

for (slug, obj) in items
  out = joinpath(BASE, slug, "systems", "Oscar.jl", "data.json")
  mkpath(dirname(out))
  save(out, obj)
  println("Generated ", slug)
end
