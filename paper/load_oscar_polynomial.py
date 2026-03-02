import json
from sage.all import PolynomialRing, QQ, prod

def load_oscar_polynomial(path):
  with open(path) as json_file:
    file_data = json.load(json_file)
    if ("Oscar" in file_data["_ns"] and
        file_data["_ns"]["Oscar"][1].startswith("1.0.")):
      t, d, refs = (file_data[k] for k in ["_type", "data", "_refs"])
      parent_ring_data = refs[t["params"]]["data"]
      base_ring = parent_ring_data["base_ring"]
      if base_ring["_type"] != "QQField":
        raise NotImplementedError("only rational coefficients supported")
      symbols = ",".join(parent_ring_data["symbols"])
      R, gens = QQ[symbols].objgens()
      p = R(0)
      for e, c in d:
        exps = [int(exponent) for exponent in e]
        coeff = QQ(c.replace("//", "/"))
        p += coeff * prod([g**i for g, i in zip(gens, exps)])
      return p
    else:
      raise RuntimeError("can only load OSCAR version 1.0 polynomials")
