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

from mocktest import *
from pyqcy import *

import neat.locals.overload.statistics as stats

import logging
logging.disable(logging.CRITICAL)


class Statistics(TestCase):

    def test_loess_factory(self):
        alg = stats.loess_factory(
            300, 20., {'threshold': 1.0, 'param': 1.2, 'length': 3})
        self.assertEqual(alg([]), (False, {}))

        data = [1.05, 1.09, 1.07, 1.12, 1.02, 1.18,
                1.15, 1.04, 1.10, 1.16, 1.08]
        self.assertEqual(alg(data), (True, {}))

        data = [0.55, 0.60, 0.62, 0.59, 0.67, 0.73, 0.85, 0.97, 0.73,
                0.68, 0.69, 0.52, 0.51, 0.55, 0.48, 0.46, 0.52, 0.55,
                0.58, 0.65, 0.70]
        self.assertEqual(alg(data), (False, {}))

    def test_loess_robust_factory(self):
        alg = stats.loess_robust_factory(
            300, 20., {'threshold': 1.0, 'param': 1.2, 'length': 3})
        self.assertEqual(alg([]), (False, {}))

        data = [1.05, 1.09, 1.07, 1.12, 1.02, 1.18,
                1.15, 1.04, 1.10, 1.16, 1.08]
        self.assertEqual(alg(data), (True, {}))

        data = [0.55, 0.60, 0.62, 0.59, 0.67, 0.73, 0.85, 0.97, 0.73,
                0.68, 0.69, 0.52, 0.51, 0.55, 0.48, 0.46, 0.52, 0.55,
                0.58, 0.65, 0.70]
        self.assertEqual(alg(data), (False, {}))

    def test_mad_threshold_factory(self):
        with MockTransaction:
            expect(stats).mad.and_return(0.125).exactly(6).times()
            alg = stats.mad_threshold_factory(
                300, 20., {'threshold': 1.6, 'limit': 3})
            self.assertEqual(alg([]), (False, {}))
            self.assertEqual(alg([0., 0., 0.0]), (False, {}))
            self.assertEqual(alg([0., 0., 0.5]), (False, {}))
            self.assertEqual(alg([0., 0., 0.6]), (False, {}))
            self.assertEqual(alg([0., 0., 0.8]), (True, {}))
            self.assertEqual(alg([0., 0., 0.9]), (True, {}))
            self.assertEqual(alg([0., 0., 1.0]), (True, {}))

    def test_iqr_threshold_factory(self):
        with MockTransaction:
            expect(stats).iqr.and_return(0.125).exactly(6).times()
            alg = stats.iqr_threshold_factory(
                300, 20., {'threshold': 1.6, 'limit': 3})
            self.assertEqual(alg([]), (False, {}))
            self.assertEqual(alg([0., 0., 0.0]), (False, {}))
            self.assertEqual(alg([0., 0., 0.5]), (False, {}))
            self.assertEqual(alg([0., 0., 0.6]), (False, {}))
            self.assertEqual(alg([0., 0., 0.8]), (True, {}))
            self.assertEqual(alg([0., 0., 0.9]), (True, {}))
            self.assertEqual(alg([0., 0., 1.0]), (True, {}))

    def test_loess(self):
        assert not stats.loess(1.0, 1.2, 3, 0.5, [])

        data = [1.05, 1.09, 1.07, 1.12, 1.02, 1.18,
                1.15, 1.04, 1.10, 1.16, 1.08]
        assert stats.loess(1.0, 1.2, 3, 0.5, data)

        data = [0.55, 0.60, 0.62, 0.59, 0.67, 0.73, 0.85, 0.97, 0.73,
                0.68, 0.69, 0.52, 0.51, 0.55, 0.48, 0.46, 0.52, 0.55,
                0.58, 0.65, 0.70]
        assert not stats.loess(1.0, 1.2, 3, 0.5, data)

    def test_loess_robust(self):
        assert not stats.loess_robust(1.0, 1.2, 3, 0.5, [])

        data = [1.05, 1.09, 1.07, 1.12, 1.02, 1.18,
                1.15, 1.04, 1.10, 1.16, 1.08]
        assert stats.loess_robust(1.0, 1.2, 3, 0.5, data)

        data = [0.55, 0.60, 0.62, 0.59, 0.67, 0.73, 0.85, 0.97, 0.73,
                0.68, 0.69, 0.52, 0.51, 0.55, 0.48, 0.46, 0.52, 0.55,
                0.58, 0.65, 0.70]
        assert not stats.loess_robust(1.0, 1.2, 3, 0.5, data)

    def test_mad_threshold(self):
        with MockTransaction:
            expect(stats).mad.and_return(0.125).exactly(6).times()
            assert not stats.mad_threshold(1., 3, [])
            assert not stats.mad_threshold(1., 3, [0., 0., 0.])
            assert not stats.mad_threshold(1.6, 3, [0., 0., 0.5])
            assert not stats.mad_threshold(1.6, 3, [0., 0., 0.6])
            assert stats.mad_threshold(1.6, 3, [0., 0., 0.8])
            assert stats.mad_threshold(1.6, 3, [0., 0., 0.9])
            assert stats.mad_threshold(1.6, 3, [0., 0., 1.0])

    def test_iqr_threshold(self):
        with MockTransaction:
            expect(stats).iqr.and_return(0.125).exactly(6).times()
            assert not stats.iqr_threshold(1., 3, [])
            assert not stats.iqr_threshold(1., 3, [0., 0., 0.])
            assert not stats.iqr_threshold(1.6, 3, [0., 0., 0.5])
            assert not stats.iqr_threshold(1.6, 3, [0., 0., 0.6])
            assert stats.iqr_threshold(1.6, 3, [0., 0., 0.8])
            assert stats.iqr_threshold(1.6, 3, [0., 0., 0.9])
            assert stats.iqr_threshold(1.6, 3, [0., 0., 1.0])

    def test_utilization_threshold_abstract(self):
        f = lambda x: 0.8
        assert not stats.utilization_threshold_abstract(f, 3, [])
        assert not stats.utilization_threshold_abstract(f, 3, [0., 0., 0.])
        assert stats.utilization_threshold_abstract(f, 3, [0., 0., 1.0])
        assert not stats.utilization_threshold_abstract(
            f, 3, [0., 0., 0., 0.])
        assert not stats.utilization_threshold_abstract(
            f, 3, [0., 0., 0., 0.5])
        assert not stats.utilization_threshold_abstract(
            f, 3, [0., 0., 0., 0.7])
        assert stats.utilization_threshold_abstract(f, 3, [0., 0., 0., 0.8])
        assert stats.utilization_threshold_abstract(f, 3, [0., 0., 0., 0.9])
        assert stats.utilization_threshold_abstract(f, 3, [0., 0., 0., 1.0])

    def test_mad(self):
        data = [1, 1, 2, 2, 4, 6, 9]
        assert stats.mad(data) == 1.

    def test_iqr(self):
        data = [105, 109, 107, 112, 102, 118, 115, 104, 110, 116, 108]
        assert stats.iqr(data) == 10.

        data = [2., 4., 7., -20., 22., -1., 0., -1., 7., 15., 8., 4.,
                -4., 11., 11., 12., 3., 12., 18., 1.]
        assert stats.iqr(data) == 12.

    def test_loess_parameter_estimates(self):
        data = [2., 4., 7., -20., 22., -1., 0., -1., 7., 15., 8., 4.,
                -4., 11., 11., 12., 3., 12., 18., 1.]
        estimates = stats.loess_parameter_estimates(data)
        self.assertAlmostEqual(estimates[0], 2.2639, 3)
        self.assertAlmostEqual(estimates[1], 0.3724, 3)

    def test_loess_robust_parameter_estimates(self):
        data = [2., 4., 7., -20., 22., -1., 0., -1., 7., 15., 8., 4.,
                -4., 11., 11., 12., 3., 12., 18., 1.]
        estimates = stats.loess_robust_parameter_estimates(data)
        self.assertAlmostEqual(estimates[0], 2.4547, 3)
        self.assertAlmostEqual(estimates[1], 0.3901, 3)

    def test_tricube_weights(self):
        for actual, expected in zip(
                stats.tricube_weights(5),
                [0.669, 0.669, 0.669, 0.953, 1.0]):
            self.assertAlmostEqual(actual, expected, 2)

        for actual, expected in zip(
                stats.tricube_weights(10),
                [0.148, 0.148, 0.148, 0.348, 0.568, 0.759,
                 0.892, 0.967, 0.995, 1.0]):
            self.assertAlmostEqual(actual, expected, 2)

    def test_tricube_bisquare_weights(self):
        for actual, expected in zip(
                stats.tricube_bisquare_weights([1., 1., 2., 2., 4., 6., 9.]),
                [0.329, 0.329, 0.329, 0.633, 0.705, 0.554, 0.191]):
            self.assertAlmostEqual(actual, expected, 2)
