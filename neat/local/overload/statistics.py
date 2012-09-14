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
from scipy import stats
from scipy.odr import *


@contract
def loess_parameter_estimates(data):
    """

    :param data: A data set.
     :type data: list(number)

    :return: The parameter estimates.
     :rtype: list(number)
    """
    x = range(1, len(data) + 1)
    slope, intercept, _, _, _ = stats.linregress(x, data)
    print slope
    print intercept

    def f(B, x):
        ''' Linear function y = a*x + b '''
        return B[0] * x + B[1]

    linear = Model(f)
    mydata = Data(x, data) #, we=weights)
    return ODR(mydata, linear, beta0=[slope, intercept]).run().beta.tolist()


@contract
def tricube_weights(n):
    """ Generates a list of weights according to the tricube function.

    :param n: The number of weights to generate.
     :type n: int

    :return: A list of generated weights.
     :rtype: list(float)
    """
    spread = top = float(n - 1)
    infinity = float('inf')
    weights = []
    for i in range(2, n):
        k = (1 - ((top - i) / spread) ** 3) ** 3
        if k > 0:
            weights.append(1 / k)
        else:
            weights.append(infinity)
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
    infinity = float('inf')
    weights2 = []
    for i in range(2, n):
        k = (1 - (data[i] / s6) ** 2) ** 2
        if k > 0:
            weights2.append(weights[i] / k)
        else:
            weights2.append(infinity)
    return [weights2[0], weights2[0]] + weights2
