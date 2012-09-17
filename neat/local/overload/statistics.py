# Copyright 2012 Anton Beloglazov
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Statistics based overload detection algorithms.
"""

from contracts import contract
from neat.contracts_extra import *

from numpy import median
from scipy.optimize import leastsq
import numpy as np


@contract
def loess_parameter_estimates(data):
    """ Calculate Loess parameter estimates.

    :param data: A data set.
     :type data: list(float)

    :return: The parameter estimates.
     :rtype: list(float)
    """
    def f(p, x, y, weights):
        return weights * (y - (p[0] + p[1] * x))

    n = len(data)
    estimates, _ = leastsq(f, [1., 1.], args=(
        np.array(range(1, n + 1)),
        np.array(data),
        np.array(tricube_weights(n))))

    return estimates.tolist()


@contract
def loess_robust_parameter_estimates(data):
    """ Calculate Loess robust parameter estimates.

    :param data: A data set.
     :type data: list(float)

    :return: The parameter estimates.
     :rtype: list(float)
    """
    def f(p, x, y, weights):
        return weights * (y - (p[0] + p[1] * x))

    n = len(data)
    x = np.array(range(1, n + 1))
    y = np.array(data)
    weights = np.array(tricube_weights(n))
    estimates, _ = leastsq(f, [1., 1.], args=(x, y, weights))

    p = estimates.tolist()
    residuals = (y - (p[0] + p[1] * x))

    weights2 = np.array(tricube_bisquare_weights(residuals.tolist()))
    estimates2, _ = leastsq(f, [1., 1.], args=(x, y, weights2))

    return estimates2.tolist()


@contract
def tricube_weights(n):
    """ Generates a list of weights according to the tricube function.

    :param n: The number of weights to generate.
     :type n: int

    :return: A list of generated weights.
     :rtype: list(float)
    """
    spread = top = float(n - 1)
    weights = []
    for i in range(2, n):
        weights.append((1 - ((top - i) / spread) ** 3) ** 3)
    return [weights[0], weights[0]] + weights


@contract
def tricube_bisquare_weights(data):
    """ Generates a list of weights according to the tricube bisquare function.

    :param data: The input data.
     :type data: list(float)

    :return: A list of generated weights.
     :rtype: list(float)
    """
    n = len(data)
    s6 = 6 * median(map(abs, data))
    weights = tricube_weights(n)
    weights2 = []
    for i in range(2, n):
            weights2.append(weights[i] * (1 - (data[i] / s6) ** 2) ** 2)
    return [weights2[0], weights2[0]] + weights2
