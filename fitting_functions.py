# ThermLUM - luminescent thermometry data analysis application
# Copyright (C) 2024  Hubert Dzielak 

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
from numpy import exp, tanh, sqrt, cosh, sinh

boltzmann_constant_J_K = 1 # values of energy in K
parameters_limit = 1e4


def single_mott_seitz(x, delta0, a1, e1):
    return delta0 / (1 + a1 * exp(-e1 / (boltzmann_constant_J_K * x)))


def single_mott_seitz_error(x, delta0, a1, e1, delta0_error, a1_error, e1_error):
    return sqrt(delta0_error**2 * (1 / (1 + a1 * exp(-e1 / (boltzmann_constant_J_K * x) + (1 + a1 * exp(-e1 / (boltzmann_constant_J_K * x))))))**2 + a1_error**2 * (exp(-e1 / (boltzmann_constant_J_K * x) * delta0 / (a1 + exp(e1 / (boltzmann_constant_J_K * x)))**2))**2 + e1_error**2 * (exp(-e1 / (boltzmann_constant_J_K * x)) * a1 * delta0 / (x * (exp(e1 / (boltzmann_constant_J_K * x)) + a1)**2))**2)


def double_mott_seitz(x, delta0, a1, a2, e1, e2):
    return delta0 / (1 + a1 * exp(-e1 / (boltzmann_constant_J_K * x) + (1 + a2 * exp(-e2 / (boltzmann_constant_J_K * x)))))


def double_mott_seitz_error(x, delta0, a1, a2, e1, e2, delta0_error, a1_error, a2_error, e1_error, e2_error):
    return sqrt(
        delta0_error**2 * (1 / (1 + a1 * exp(-e1 / (boltzmann_constant_J_K * x) + (1 + a2 * exp(-e2 / (boltzmann_constant_J_K * x)))))) + 
        a1_error**2 * (exp(-e1 / (boltzmann_constant_J_K * x) * delta0 / (a1 * exp(-e1 / (boltzmann_constant_J_K * x)) + a2 * exp(-e2 / (boltzmann_constant_J_K * x)) + 1)**2))**2 + 
        a2_error**2 * (exp(-e1 / (boltzmann_constant_J_K * x) * delta0 / (a1 * exp(-e1 / (boltzmann_constant_J_K * x)) + a2 * exp(-e2 / (boltzmann_constant_J_K * x)) + 1)**2))**2 + 
        e1_error**2 * (a1 * delta0 * exp(-e1 / (boltzmann_constant_J_K * x) / (x * ((a1 * exp(-e1 / (boltzmann_constant_J_K * x)) + a2 * exp(-e2 / (boltzmann_constant_J_K * x)) + 1)**2))))**2 +
        e2_error**2 * (a2 * delta0 * exp(-e2 / (boltzmann_constant_J_K * x) / (x * ((a1 * exp(-e1 / (boltzmann_constant_J_K * x)) + a2 * exp(-e2 / (boltzmann_constant_J_K * x)) + 1)**2))))**2)


def linear(x, a, b):
    return a * x + b

def linear_error(x, a, b, a_error, b_error):
    return sqrt(a_error**2 * x**2 + b_error**2)


def exponential_decay(x, b, e1):
    return b * exp(-e1 / (boltzmann_constant_J_K * x))


def exponential_decay_error(x, b, e1, b_error, e1_error):
    return sqrt(b_error**2 * exp(-e1 / (boltzmann_constant_J_K * x))**2 + 
                e1_error**2 * (b * exp(-e1 / (boltzmann_constant_J_K * x)) / x)**2)


def coth_vibration(x, delta0, ev, b):
    return delta0 / ((1 / tanh(ev / (2 * x))) + b)

def coth_vibration_error(x, delta0, ev, b, delta0_error, ev_error, b_error):
    return sqrt(delta0_error**2 * (1 / (1 / tanh(ev / (2 * x)) + b))**2 +
                ev_error**2 * ((delta0 / (2 * x * (b * sinh(ev / (2 * x)) + cosh(ev / 2 * x)**2))))**2 +
                b_error**2 * (delta0 / (b + 1 / tanh(ev / (2 * x)))**2)**2)


dict_of_fitting_functions = {
    'Single Mott-Seitz': single_mott_seitz,
    'Double Mott-Seitz': double_mott_seitz,
    'Linear': linear,
    'Exponential decay': exponential_decay,
    'coth': coth_vibration
}

dict_of_fitting_limits = {
    'Single Mott-Seitz': [[-parameters_limit, 0, 0], [parameters_limit, parameters_limit, parameters_limit]],
    'Double Mott-Seitz': [[-parameters_limit, 0, 0, 0, 0], [parameters_limit, parameters_limit, parameters_limit, parameters_limit, parameters_limit]],
    'Linear': [[-parameters_limit, -parameters_limit], [parameters_limit, parameters_limit]],
    'Exponential decay': [[-parameters_limit, 0], [parameters_limit, parameters_limit]],
    'coth': [[-parameters_limit, 0, -parameters_limit], [parameters_limit, parameters_limit, parameters_limit]]
}

dict_of_fitting_errors_functions = {
    'Single Mott-Seitz': single_mott_seitz_error,
    'Double Mott-Seitz': double_mott_seitz_error,
    'Linear': linear_error,
    'Exponential decay': exponential_decay_error,
    'coth': coth_vibration_error
}

