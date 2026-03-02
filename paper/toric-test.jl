@testset "ToricDivisor" begin
  pp = projective_space(NormalToricVariety, 2)
  td0 = toric_divisor(pp, [1,1,2])
  td1 = toric_divisor(pp, [1,1,3])
  vtd = [td0, td1]
  test_save_load_roundtrip(path, vtd) do loaded
    @test coefficients(td0) == coefficients(loaded[1])
    @test coefficients(td1) == coefficients(loaded[2])
    @test toric_variety(loaded[1]) == toric_variety(loaded[2])
  end
end
