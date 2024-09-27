from numpy import exp, tanh, inf

boltzmann_constant_J_K = 1.380649e-23


def single_mott_seitz(x, delta0, a1, e1):
    return delta0 / (1 + a1 * exp(-e1 / (boltzmann_constant_J_K * x)))


def double_mott_seitz(x, delta0, a1, a2, e1, e2):
    return delta0 / (1 + a1 * exp(-e1 / (boltzmann_constant_J_K * x) + (1 + a2 * exp(-e2 / (boltzmann_constant_J_K * x)))))


def linear(x, a, b):
    return a * x + b


def exponential_decay(x, b, e1):
    return b * exp(-e1 / (boltzmann_constant_J_K * x))


def coth_vibration(x, delta0, ev, b):
    return delta0 / ((1 / tanh(ev / (2 * x))) + b)


dict_of_fitting_functions = {
    'Single Mott-Seitz': single_mott_seitz,
    'Double Mott-Seitz': double_mott_seitz,
    'Linear': linear,
    'Exponential decay': exponential_decay,
    'coth': coth_vibration
}

dict_of_fitting_limits = {
    'Single Mott-Seitz': [[-inf, 0, 0], [inf, inf, inf]],
    'Double Mott-Seitz': [[-inf, 0, 0, 0, 0], [inf, inf, inf, inf, inf]],
    'Linear': [[-inf, -inf], [inf, inf]],
    'Exponential decay': [[-inf, 0], [inf, inf]],
    'coth': [[-inf, 0, -inf], [inf, inf, inf]]
}

