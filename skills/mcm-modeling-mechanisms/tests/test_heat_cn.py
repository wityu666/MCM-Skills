import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec = importlib.util.spec_from_file_location("modeling_heat_cn", Path(__file__).parents[1] / "scripts/heat_cn.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
heat_cn = module.heat_cn


def test_sine_solution_and_second_order_spatial_refinement():
    errors = []
    for nx, nt in ((20, 100), (40, 400)):
        x, t, U = heat_cn(lambda z: np.sin(np.pi * z), .3, 1., .2, nx, nt)
        exact = np.sin(np.pi * x) * np.exp(-.3 * np.pi**2 * t[-1])
        errors.append(np.max(np.abs(U[-1] - exact)))
        assert np.max(np.abs(U[:, [0, -1]])) == 0
    assert errors[1] < 0.001
    assert 3.5 < errors[0] / errors[1] < 4.5


def test_zero_field_and_zero_diffusivity():
    _, _, U = heat_cn(np.zeros(7), .8, 2., .4, 6, 5)
    np.testing.assert_array_equal(U, 0.)
    _, _, U = heat_cn([0., 1., 2., 1., 0.], 0., 1., .2, 4, 3)
    np.testing.assert_array_equal(U, np.tile([0., 1., 2., 1., 0.], (4, 1)))


def test_discrete_energy_nonincrease_for_large_time_steps():
    initial = np.array([0., .4, 1.2, -.8, .7, -.2, 0.])
    _, _, U = heat_cn(initial, 2., 1., 1., 6, 4)
    energy = np.sum(U**2, axis=1)
    assert np.all(np.diff(energy) <= 100*np.finfo(float).eps*energy[0])


@pytest.mark.parametrize("kwargs", [{"nx":1}, {"nt":0}, {"diffusivity":-1}, {"length":0}, {"final_time":np.nan}])
def test_reject_invalid_problem_definition(kwargs):
    args = dict(initial=lambda z: np.sin(np.pi*z), diffusivity=.3, length=1., final_time=.2, nx=4, nt=5)
    args.update(kwargs)
    with pytest.raises(ValueError): heat_cn(**args)


def test_nonzero_boundary_and_nonfinite_input_rejected():
    with pytest.raises(ValueError): heat_cn([1., 0., 0.], .3, 1., .2, 2, 5)
    with pytest.raises(ValueError): heat_cn([0., np.nan, 0.], .3, 1., .2, 2, 5)


def test_complex_initial_and_nonscalar_coefficients_rejected():
    with pytest.raises(ValueError): heat_cn(np.array([0.,1+100j,0.]), .3, 1., .2, 2, 5)
    for value in ([.3], '0.3', True, 1j):
        with pytest.raises(ValueError): heat_cn([0.,1.,0.], value, 1., .2, 2, 5)


def test_representable_ratio_survives_underflowing_products():
    # One interior point: CN multiplier (1-r)/(1+r), r=4.
    _, _, U = heat_cn([0.,1.,0.], 1e-300, 1e-200, 1e-100, 2, 1)
    np.testing.assert_allclose(U[-1], [0.,-.6,0.], atol=1e-14)


def test_zero_diffusivity_and_overflowing_step_products():
    _, _, U = heat_cn([0.,1.,0.], 0., 1e-200, 1., 2, 1)
    np.testing.assert_array_equal(U, [[0.,1.,0.],[0.,1.,0.]])
    _, _, U = heat_cn([0.,1.,0.], 1e308, 1e308, 1e308, 2, 1)
    np.testing.assert_allclose(U[-1], [0.,-.6,0.], atol=1e-14)


def test_unrepresentable_grid_and_ratio_rejected():
    with pytest.raises(ValueError): heat_cn([0.,1.,0.], .1, np.nextafter(0.,1.), 1., 2, 1)
    with pytest.raises(ValueError): heat_cn([0.,1.,0.], 1e308, 1e-100, 1e308, 2, 1)
