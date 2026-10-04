import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec = importlib.util.spec_from_file_location("modeling_entropy_topsis", Path(__file__).parents[1] / "scripts/entropy_topsis.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_hand_calculable_two_indicator_example():
    # Both oriented indicators are [0, 1/2, 1]; their relative distances agree.
    result = module.entropy_topsis([[1.,3.],[2.,2.],[3.,1.]], [True,False])
    np.testing.assert_allclose(result["weights"], [.5,.5], atol=1e-14)
    np.testing.assert_allclose(result["scores"], [0.,.5,1.], atol=1e-14)


def test_zero_constant_columns_have_zero_weight():
    result = module.entropy_topsis([[1.,0.,8.],[2.,0.,8.],[3.,0.,8.]])
    np.testing.assert_allclose(result["weights"], [1.,0.,0.])
    np.testing.assert_allclose(result["scores"], [0.,.5,1.])
    np.testing.assert_allclose(result["entropy_profile"]["probabilities"].sum(axis=0), 1.)


def test_all_constant_objects_have_no_ranking_information():
    result = module.entropy_topsis(np.full((4,3), 7.))
    assert result["status"] == "NO_DISCRIMINATION"
    np.testing.assert_array_equal(result["weights"], 0.)
    np.testing.assert_array_equal(result["scores"], .5)


def test_row_permutation_and_positive_affine_unit_invariance():
    X = np.array([[2.,8.,-3.],[5.,3.,1.],[8.,6.,7.],[4.,4.,2.]])
    base = module.entropy_topsis(X, [True,False,True])
    perm = [2,0,3,1]
    permuted = module.entropy_topsis(X[perm], [True,False,True])
    changed_units = module.entropy_topsis(X*np.array([100.,.1,2.])+[7.,-5.,3.], [True,False,True])
    np.testing.assert_allclose(permuted["scores"], base["scores"][perm], atol=1e-14)
    np.testing.assert_allclose(changed_units["scores"], base["scores"], atol=1e-14)
    assert np.all((base["scores"]>=0)&(base["scores"]<=1))
    assert np.all(base["weights"]>=0)
    np.testing.assert_allclose(base["weights"].sum(), 1.)


@pytest.mark.parametrize("bad", [[[1.,2.]], [[np.nan],[2.]], [[np.inf],[2.]]])
def test_invalid_data_rejected(bad):
    with pytest.raises(ValueError): module.entropy_topsis(bad)


def test_invalid_weights_and_direction_rejected():
    with pytest.raises(ValueError): module.topsis([[1.,2.],[2.,3.]], [-1.,2.])
    with pytest.raises(ValueError): module.topsis([[1.,2.],[2.,3.]], [0.,0.])
    with pytest.raises(ValueError): module.entropy_topsis([[1.],[2.]], [1])


def test_large_finite_weights_preserve_normalized_ranking():
    X = [[1.,3.],[2.,2.],[3.,1.]]
    ordinary = module.topsis(X, [1.,1.], [True,False])
    large = module.topsis(X, [1e308,1e308], [True,False])
    np.testing.assert_allclose(large["weights"], ordinary["weights"])
    np.testing.assert_allclose(large["scores"], ordinary["scores"])
    assert large["status"] == "OK"


def test_known_uniform_and_point_mass_entropy_limits():
    profile = module.entropy_profile([[3.,0.],[3.,1.]])
    np.testing.assert_allclose(profile["probabilities"], [[.5,0.],[.5,1.]])
    np.testing.assert_allclose(profile["entropy"], [1.,0.])
    np.testing.assert_allclose(profile["weights"], [0.,1.])


def test_tiny_nonzero_weight_preserves_one_indicator_ranking():
    # A constant second indicator contributes no ideal distance.
    result = module.topsis([[1.,7.],[2.,7.],[3.,7.]], [1e-200,1.])
    np.testing.assert_allclose(result['scores'], [0.,.5,1.], atol=1e-14)
    assert result['status'] == 'OK'
    assert np.all(np.isfinite(result['distance_best']))


def test_subnormal_weight_does_not_quantize_the_closeness_ratio():
    result = module.topsis([[1.,7.],[2.,7.],[3.,7.]], [np.nextafter(0.,1.),1.])
    np.testing.assert_allclose(result['scores'], [0.,.5,1.], atol=1e-14)
    np.testing.assert_allclose(result['scaled_distance_best'][1], result['scaled_distance_worst'][1])


def test_unrepresentable_active_weight_ratio_fails_explicitly():
    with pytest.raises(ValueError): module.topsis([[1.,7.],[2.,7.]], [1e-100,1e308])


def test_complex_inputs_are_not_silently_projected_to_real():
    with pytest.raises(ValueError): module.entropy_topsis(np.array([[1+100j],[2+200j]]))
    with pytest.raises(ValueError): module.topsis([[1.],[2.]], np.array([1+2j]))
