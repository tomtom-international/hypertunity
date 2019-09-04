import numpy as np

from hypertunity.optimisation import EvaluationScore

SIMPLE_CONT_FUNC_ARGMAX = 3.989333
SIMPLE_CONT_FUNC_MAX = 5.958363


def simple_continuous_func(x):
    """Compute x * sin(2x) + 2 if x in [0, 5] else 0."""
    fx = np.atleast_1d(x * np.sin(2 * x) + 2)
    fx[np.logical_and(x < 0, x > 5)] = 0.
    return fx


SIMPLE_MIXED_FUNC_ARGMAX = (6.0, "sqr", 0)
SIMPLE_MIXED_FUNC_MAX = 36.0


def simple_mixed_func(x, y, z):
    """Compute `simple_continuous_func` + z if y == 'sin', else return x**2 - 3 * z
    where x is continuous, y is categorical ("sin", "sqr"), z is discrete.

    Args:
        x: float or np.ndarray, continuous variable         [-5.0, 6.0]
        y: str, categorical variable                        ("sin", "sqr")
        z: float or int or np.ndarray, discrete variable    (0, 1, 2, 3)
    """
    if y == "sin":
        return (simple_continuous_func(x) + z)[0]
    elif y == "sqr" and z in [0, 1, 2, 3]:
        return x ** 2 - 3 * z
    else:
        raise ValueError("`y` can only be 'sin' or 'sqr' and z [0, 1, 2, 3].")


SIMPLE_DISCRETE_FUNC_ARGMAX = (4, 5, "large")
SIMPLE_DISCRETE_FUNC_MAX = 3.0


def simple_discrete_func(x, y, z):
    """Compute c * x * y where c = 0.1 if z == "small" else 0.15.

    `x` and `y` are discrete numerical values, z is categorical.

    Args:
        x: int, discrete variable                           (1, 2, 3, 4)
        y: int, discrete variable                           (-3, 2, 5)
        z: str, categorical variable                        ("small", "large")
    """
    if x not in {1, 2, 3, 4} and y not in {-3, 2, 5} and z not in {"small", "large"}:
        raise ValueError("Outside the allowed domain.")
    if z == "small":
        return 0.1 * x * y
    return 0.15 * x * y


def evaluate_simple_continuous(opt, batch_size, n_steps):
    all_samples = []
    all_evaluations = []
    for i in range(n_steps):
        samples = opt.run_step(batch_size)
        evaluations = simple_continuous_func(np.array([s["x"] for s in samples]))
        opt.update(samples, [EvaluationScore(ev) for ev in evaluations], )
        # gather the samples and evaluations for later assessment
        all_samples.extend([s["x"] for s in samples])
        all_evaluations.extend(evaluations)
    best_eval_index = int(np.argmax(all_evaluations))
    best_sample = all_samples[best_eval_index]
    best_eval = all_evaluations[best_eval_index]
    assert np.isclose(best_sample, SIMPLE_CONT_FUNC_ARGMAX, atol=1e-1)
    assert np.isclose(best_eval, SIMPLE_CONT_FUNC_MAX, atol=1e-1)


def evaluate_simple_mixed(opt, batch_size, n_steps):
    all_samples = []
    all_evaluations = []
    for i in range(n_steps):
        samples = opt.run_step(batch_size)
        evaluations = [simple_mixed_func(s["x"], s["y"], s["z"]) for s in samples]
        opt.update(samples, [EvaluationScore(ev) for ev in evaluations], )
        # gather the samples and evaluations for later assessment
        all_samples.extend([(s["x"], s["y"], s["z"]) for s in samples])
        all_evaluations.extend(evaluations)
    best_eval_index = int(np.argmax(all_evaluations))
    best_sample = all_samples[best_eval_index]
    best_eval = all_evaluations[best_eval_index]
    assert np.isclose(best_sample[0], SIMPLE_MIXED_FUNC_ARGMAX[0], atol=1.0)
    assert best_sample[1:] == SIMPLE_MIXED_FUNC_ARGMAX[1:]
    assert np.isclose(best_eval, SIMPLE_MIXED_FUNC_MAX, atol=1.0)


def evaluate_simple_discrete(opt, batch_size, n_steps):
    all_samples = []
    all_evaluations = []
    for i in range(n_steps):
        samples = opt.run_step(batch_size)
        evaluations = [simple_discrete_func(s["x"], s["y"], s["z"]) for s in samples]
        opt.update(samples, [EvaluationScore(ev) for ev in evaluations], )
        # gather the samples and evaluations for later assessment
        all_samples.extend([(s["x"], s["y"], s["z"]) for s in samples])
        all_evaluations.extend(evaluations)
    best_eval_index = int(np.argmax(all_evaluations))
    best_sample = all_samples[best_eval_index]
    best_eval = all_evaluations[best_eval_index]
    assert best_sample == SIMPLE_DISCRETE_FUNC_ARGMAX
    assert best_eval == SIMPLE_DISCRETE_FUNC_MAX
