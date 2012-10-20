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

from collections import deque
from copy import deepcopy
import re

import neat.locals.overload.mhod.multisize_estimation as m

import logging
logging.disable(logging.CRITICAL)


def c(data):
    return deepcopy(data)


class Multisize(TestCase):

    def test_mean(self):
        self.assertEqual(m.mean([], 100), 0.0)
        self.assertEqual(m.mean([0], 100), 0.0)
        self.assertEqual(m.mean([0, 0], 100), 0.0)
        self.assertEqual(m.mean([1, 1], 100), 0.02)
        self.assertEqual(m.mean([0, 1], 100), 0.01)
        self.assertEqual(m.mean([1, 2, 3, 4, 5], 100), 0.15)

    def test_variance(self):
        self.assertEqual(m.variance([], 100), 0.0)
        self.assertEqual(m.variance([0], 100), 0.0)
        self.assertEqual(m.variance([0, 0], 100), 0.0)
        self.assertAlmostEqual(m.variance([1, 1], 100), 0.0194020202)
        self.assertAlmostEqual(m.variance([0, 1], 100), 0.0099010101)
        self.assertAlmostEqual(m.variance([1, 2, 3, 4, 5], 100), 0.511237373)
        self.assertAlmostEqual(m.variance([0, 0, 0, 1], 100), 0.0099030303)

    def test_acceptable_variance(self):
        self.assertAlmostEqual(m.acceptable_variance(0.2, 5), 0.032, 3)
        self.assertAlmostEqual(m.acceptable_variance(0.6, 15), 0.016, 3)

    def test_estimate_probability(self):
        self.assertEqual(
            m.estimate_probability([0, 0, 1, 1, 0, 0, 0, 0, 0, 0], 100, 0),
            0.08)
        self.assertEqual(
            m.estimate_probability([0, 0, 1, 1, 0, 0, 0, 0, 0, 0], 100, 1),
            0.02)
        self.assertEqual(
            m.estimate_probability([1, 1, 0, 0, 1, 1, 1, 1, 1, 1], 200, 0),
            0.01)
        self.assertEqual(
            m.estimate_probability([1, 1, 0, 0, 1, 1, 1, 1, 1, 1], 200, 1),
            0.04)

    def test_update_request_windows(self):
        max_window_size = 4
        windows = [deque([0, 0], max_window_size),
                   deque([1, 1], max_window_size)]

        self.assertEqual(m.update_request_windows(c(windows), 0, 0),
                         [deque([0, 0, 0]),
                          deque([1, 1])])
        self.assertEqual(m.update_request_windows(c(windows), 0, 1),
                         [deque([0, 0, 1]),
                          deque([1, 1])])
        self.assertEqual(m.update_request_windows(c(windows), 1, 0),
                         [deque([0, 0]),
                          deque([1, 1, 0])])
        self.assertEqual(m.update_request_windows(c(windows), 1, 1),
                         [deque([0, 0]),
                          deque([1, 1, 1])])

        max_window_size = 2
        windows = [deque([0, 0], max_window_size),
                   deque([1, 1], max_window_size)]

        self.assertEqual(m.update_request_windows(c(windows), 0, 0),
                         [deque([0, 0]),
                          deque([1, 1])])
        self.assertEqual(m.update_request_windows(c(windows), 0, 1),
                         [deque([0, 1]),
                          deque([1, 1])])
        self.assertEqual(m.update_request_windows(c(windows), 1, 0),
                         [deque([0, 0]),
                          deque([1, 0])])
        self.assertEqual(m.update_request_windows(c(windows), 1, 1),
                         [deque([0, 0]),
                          deque([1, 1])])

        max_window_size = 4
        windows = [deque([0, 0], max_window_size),
                   deque([1, 1], max_window_size),
                   deque([2, 2], max_window_size)]

        self.assertEqual(m.update_request_windows(c(windows), 0, 0),
                         [deque([0, 0, 0]),
                          deque([1, 1]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 0, 1),
                         [deque([0, 0, 1]),
                          deque([1, 1]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 0, 2),
                         [deque([0, 0, 2]),
                          deque([1, 1]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 1, 0),
                         [deque([0, 0]),
                          deque([1, 1, 0]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 1, 1),
                         [deque([0, 0]),
                          deque([1, 1, 1]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 1, 2),
                         [deque([0, 0]),
                          deque([1, 1, 2]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 2, 0),
                         [deque([0, 0]),
                          deque([1, 1]),
                          deque([2, 2, 0])])
        self.assertEqual(m.update_request_windows(c(windows), 2, 1),
                         [deque([0, 0]),
                          deque([1, 1]),
                          deque([2, 2, 1])])
        self.assertEqual(m.update_request_windows(c(windows), 2, 2),
                         [deque([0, 0]),
                          deque([1, 1]),
                          deque([2, 2, 2])])

        max_window_size = 2
        windows = [deque([0, 0], max_window_size),
                   deque([1, 1], max_window_size),
                   deque([2, 2], max_window_size)]

        self.assertEqual(m.update_request_windows(c(windows), 0, 0),
                         [deque([0, 0]),
                          deque([1, 1]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 0, 1),
                         [deque([0, 1]),
                          deque([1, 1]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 0, 2),
                         [deque([0, 2]),
                          deque([1, 1]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 1, 0),
                         [deque([0, 0]),
                          deque([1, 0]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 1, 1),
                         [deque([0, 0]),
                          deque([1, 1]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 1, 2),
                         [deque([0, 0]),
                          deque([1, 2]),
                          deque([2, 2])])
        self.assertEqual(m.update_request_windows(c(windows), 2, 0),
                         [deque([0, 0]),
                          deque([1, 1]),
                          deque([2, 0])])
        self.assertEqual(m.update_request_windows(c(windows), 2, 1),
                         [deque([0, 0]),
                          deque([1, 1]),
                          deque([2, 1])])
        self.assertEqual(m.update_request_windows(c(windows), 2, 2),
                         [deque([0, 0]),
                          deque([1, 1]),
                          deque([2, 2])])

    def test_update_estimate_windows(self):
        req_win = [deque([1, 0, 0, 0]),
                   deque([1, 0, 1, 0])]
        est_win = [[{2: deque([0, 0], 2),
                     4: deque([0, 0], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 0], 4)}],
                   [{2: deque([0, 0], 2),
                     4: deque([0, 0], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 0], 4)}]]

        self.assertEqual(
            m.update_estimate_windows(c(est_win), c(req_win), 0),
            [[{2: deque([0, 1.0]),
               4: deque([0, 0, 0.75])},
              {2: deque([0, 0.0]),
               4: deque([0, 0, 0.25])}],
             [{2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])}]])
        self.assertEqual(
            m.update_estimate_windows(c(est_win), c(req_win), 1),
            [[{2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])}],
             [{2: deque([0, 0.5]),
               4: deque([0, 0, 0.5])},
              {2: deque([0, 0.5]),
               4: deque([0, 0, 0.5])}]])

        req_win = [deque([1, 0, 2, 0]),
                   deque([1, 0, 1, 0]),
                   deque([2, 2, 1, 0])]
        est_win = [[{2: deque([0, 0], 2),
                     4: deque([0, 0], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 0], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 0], 4)}],
                   [{2: deque([0, 0], 2),
                     4: deque([0, 0], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 0], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 0], 4)}],
                   [{2: deque([0, 0], 2),
                     4: deque([0, 0], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 0], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 0], 4)}]]

        self.assertEqual(
            m.update_estimate_windows(c(est_win), c(req_win), 0),
            [[{2: deque([0, 0.5]),
               4: deque([0, 0, 0.5])},
              {2: deque([0, 0.0]),
               4: deque([0, 0, 0.25])},
              {2: deque([0, 0.5]),
               4: deque([0, 0, 0.25])}],
             [{2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])}],
             [{2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])}]])
        self.assertEqual(
            m.update_estimate_windows(c(est_win), c(req_win), 1),
            [[{2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])}],
             [{2: deque([0, 0.5]),
               4: deque([0, 0, 0.5])},
              {2: deque([0, 0.5]),
               4: deque([0, 0, 0.5])},
              {2: deque([0, 0.0]),
               4: deque([0, 0, 0.0])}],
             [{2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])}]])
        self.assertEqual(
            m.update_estimate_windows(c(est_win), c(req_win), 2),
            [[{2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])}],
             [{2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])},
              {2: deque([0, 0]),
               4: deque([0, 0])}],
             [{2: deque([0, 0.5]),
               4: deque([0, 0, 0.25])},
              {2: deque([0, 0.5]),
               4: deque([0, 0, 0.25])},
              {2: deque([0, 0.0]),
               4: deque([0, 0, 0.5])}]])

    def test_update_variances(self):
        est_win = [[{2: deque([0, 0.5], 2),
                     4: deque([1, 0, 0, 0], 4)},
                    {2: deque([1.0, 0.5], 2),
                     4: deque([0, 1, 1, 1], 4)}],
                   [{2: deque([0.5, 0.25], 2),
                     4: deque([0.25, 0.25, 0.5, 0.5], 4)},
                    {2: deque([0.5, 0.75], 2),
                     4: deque([0.75, 0.75, 0.5, 0.5], 4)}]]
        variances = [[{2: 0,
                       4: 0},
                      {2: 0,
                       4: 0}],
                     [{2: 0,
                       4: 0},
                      {2: 0,
                       4: 0}]]

        self.assertEqual(m.update_variances(c(variances), c(est_win), 0),
                         [[{2: 0.125,
                            4: 0.25},
                           {2: 0.125,
                            4: 0.25}],
                          [{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}]])
        self.assertEqual(m.update_variances(c(variances), c(est_win), 1),
                         [[{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}],
                          [{2: 0.03125,
                            4: 0.020833333333333332},
                           {2: 0.03125,
                            4: 0.020833333333333332}]])
        self.assertEqual(m.update_variances(
            m.update_variances(c(variances), c(est_win), 0), c(est_win), 0),
                         [[{2: 0.125,
                            4: 0.25},
                           {2: 0.125,
                            4: 0.25}],
                          [{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}]])

        est_win = [[{2: deque([0, 0], 2),
                     4: deque([1, 0, 0, 0], 4)},
                    {2: deque([1, 1], 2),
                     4: deque([0, 0, 1, 1], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 1, 0, 0], 4)}],
                   [{2: deque([0.5, 0.25], 2),
                     4: deque([0.25, 0.05, 0.5, 0.25], 4)},
                    {2: deque([0.25, 0.5], 2),
                     4: deque([0.4, 0.55, 0.25, 0.5], 4)},
                    {2: deque([0.25, 0.25], 2),
                     4: deque([0.35, 0.4, 0.25, 0.25], 4)}],
                   [{2: deque([1, 0], 2),
                     4: deque([1, 0, 1, 0], 4)},
                    {2: deque([0, 1], 2),
                     4: deque([0, 0, 0, 1], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 1, 0, 0], 4)}]]
        variances = [[{2: 0,
                       4: 0},
                      {2: 0,
                       4: 0},
                      {2: 0,
                       4: 0}],
                     [{2: 0,
                       4: 0},
                      {2: 0,
                       4: 0},
                      {2: 0,
                       4: 0}],
                     [{2: 0,
                       4: 0},
                      {2: 0,
                       4: 0},
                      {2: 0,
                       4: 0}]]

        self.assertEqual(m.update_variances(c(variances), c(est_win), 0),
                         [[{2: 0.0,
                            4: 0.25},
                           {2: 0.0,
                            4: 0.3333333333333333},
                           {2: 0.0,
                            4: 0.25}],
                          [{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}],
                          [{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}]])
        self.assertEqual(m.update_variances(c(variances), c(est_win), 1),
                         [[{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}],
                          [{2: 0.03125,
                            4: 0.03395833333333333},
                           {2: 0.03125,
                            4: 0.0175},
                           {2: 0.0,
                            4: 0.005625000000000001}],
                          [{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}]])
        self.assertEqual(m.update_variances(c(variances), c(est_win), 2),
                         [[{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}],
                          [{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}],
                          [{2: 0.5,
                            4: 0.3333333333333333},
                           {2: 0.5,
                            4: 0.25},
                           {2: 0.0,
                            4: 0.25}]])

    def test_update_acceptable_variances(self):
        est_win = [[{2: deque([0, 0.5], 2),
                     4: deque([1, 0, 0, 0], 4)},
                    {2: deque([1.0, 0.5], 2),
                     4: deque([0, 1, 1, 1], 4)}],
                   [{2: deque([0.5, 0.25], 2),
                     4: deque([0.25, 0.25, 0.5, 0.5], 4)},
                    {2: deque([0.5, 0.75], 2),
                     4: deque([0.75, 0.75, 0.5, 0.5], 4)}]]
        acc_variances = [[{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}],
                         [{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}]]

        self.assertEqual(m.update_acceptable_variances(c(acc_variances),
                                                       c(est_win), 0),
                         [[{2: 0.125,
                            4: 0.0},
                           {2: 0.125,
                            4: 0.0}],
                          [{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}]])
        self.assertEqual(m.update_acceptable_variances(c(acc_variances),
                                                       c(est_win), 1),
                         [[{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}],
                          [{2: 0.09375,
                            4: 0.0625},
                           {2: 0.09375,
                            4: 0.0625}]])
        self.assertEqual(m.update_acceptable_variances(
            m.update_acceptable_variances(
                c(acc_variances), c(est_win), 0), c(est_win), 0),
                         [[{2: 0.125,
                            4: 0.0},
                           {2: 0.125,
                            4: 0.0}],
                          [{2: 0,
                            4: 0},
                           {2: 0,
                            4: 0}]])

        est_win = [[{2: deque([0, 0], 2),
                     4: deque([1, 0, 0, 0], 4)},
                    {2: deque([1, 1], 2),
                     4: deque([0, 0, 1, 1], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 1, 0, 0], 4)}],
                   [{2: deque([0.5, 0.25], 2),
                     4: deque([0.25, 0.05, 0.5, 0.25], 4)},
                    {2: deque([0.25, 0.5], 2),
                     4: deque([0.4, 0.55, 0.25, 0.5], 4)},
                    {2: deque([0.25, 0.25], 2),
                     4: deque([0.35, 0.4, 0.25, 0.25], 4)}],
                   [{2: deque([1, 0], 2),
                     4: deque([1, 0, 1, 0], 4)},
                    {2: deque([0, 1], 2),
                     4: deque([0, 0, 0, 1], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 1, 0, 0], 4)}]]
        acc_variances = [[{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}],
                         [{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}],
                         [{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}]]

        self.assertEqual(m.update_acceptable_variances(c(acc_variances),
                                                       c(est_win), 0),
                        [[{2: 0.0,
                           4: 0.0},
                          {2: 0.0,
                           4: 0.0},
                          {2: 0.0,
                           4: 0.0}],
                         [{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}],
                         [{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}]])
        self.assertEqual(m.update_acceptable_variances(c(acc_variances),
                                                       c(est_win), 1),
                        [[{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}],
                         [{2: 0.09375,
                           4: 0.046875},
                          {2: 0.125,
                           4: 0.0625},
                          {2: 0.09375,
                           4: 0.046875}],
                         [{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}]])
        self.assertEqual(m.update_acceptable_variances(c(acc_variances),
                                                       c(est_win), 2),
                        [[{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}],
                         [{2: 0,
                           4: 0},
                          {2: 0,
                           4: 0},
                          {2: 0,
                           4: 0}],
                         [{2: 0.0,
                           4: 0.0},
                          {2: 0.0,
                           4: 0.0},
                          {2: 0.0,
                           4: 0.0}]])

    def test_select_window(self):
        variances = [[{2: 0.2,
                       4: 0.9},
                      {2: 0.2,
                       4: 0.6}],
                     [{2: 0.2,
                       4: 0},
                      {2: 0.2,
                       4: 0.8}]]
        acc_variances = [[{2: 0.1,
                           4: 0.5},
                          {2: 0.4,
                           4: 0.5}],
                         [{2: 0.4,
                           4: 0.5},
                          {2: 0.1,
                           4: 0.5}]]
        window_sizes = [2, 4]

        self.assertEqual(
            m.select_window(variances, acc_variances, window_sizes),
                         [[2, 2],
                          [4, 2]])

        variances = [[{2: 0,
                       4: 0.9},
                      {2: 0,
                       4: 0}],
                     [{2: 0,
                       4: 0},
                      {2: 0,
                       4: 0.8}]]
        acc_variances = [[{2: 0.5,
                           4: 0.5},
                          {2: 0.6,
                           4: 0.5}],
                         [{2: 0.7,
                           4: 0.5},
                          {2: 0.4,
                           4: 0.5}]]
        window_sizes = [2, 4]

        self.assertEqual(
            m.select_window(variances, acc_variances, window_sizes),
                         [[2, 4],
                          [4, 2]])

        variances = [[{2: 0,
                       4: 0.9},
                      {2: 0,
                       4: 0},
                      {2: 0,
                       4: 1.0}],
                     [{2: 0,
                       4: 0},
                      {2: 0,
                       4: 0.8},
                      {2: 0,
                       4: 0}],
                     [{2: 0,
                       4: 0},
                      {2: 0,
                       4: 0.8},
                      {2: 0.5,
                       4: 0}]]
        acc_variances = [[{2: 0.5,
                           4: 0.9},
                          {2: 0.6,
                           4: 0.9},
                          {2: 0.6,
                           4: 0.9}],
                         [{2: 0.7,
                           4: 0.9},
                          {2: 0.4,
                           4: 0.9},
                          {2: 0.4,
                           4: 0.9}],
                         [{2: 0.7,
                           4: 0.9},
                          {2: 0.4,
                           4: 0.5},
                          {2: 0.4,
                           4: 0.9}]]
        window_sizes = [2, 4]

        self.assertEqual(
            m.select_window(variances, acc_variances, window_sizes),
                         [[4, 4, 2],
                          [4, 4, 4],
                          [4, 2, 2]])

    def test_select_best_estimates(self):
        est_win = [[{2: deque([0, 0], 2),
                     4: deque([1, 0, 0, 0], 4)},
                    {2: deque([1, 1], 2),
                     4: deque([0, 0, 1, 1], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 1, 0, 0], 4)}],
                   [{2: deque([0.5, 0.25], 2),
                     4: deque([0.25, 0.05, 0.5, 0.25], 4)},
                    {2: deque([0.25, 0.5], 2),
                     4: deque([0.4, 0.55, 0.25, 0.6], 4)},
                    {2: deque([0.25, 0.25], 2),
                     4: deque([0.35, 0.4, 0.25, 0.15], 4)}],
                   [{2: deque([1, 0], 2),
                     4: deque([1, 0, 1, 0], 4)},
                    {2: deque([0, 1], 2),
                     4: deque([0, 0, 0, 0.2], 4)},
                    {2: deque([0, 0], 2),
                     4: deque([0, 1, 0, 0], 4)}]]
        selected_windows1 = [[2, 4, 2],
                             [2, 2, 4],
                             [4, 2, 2]]
        selected_windows2 = [[4, 4, 4],
                             [2, 2, 2],
                             [2, 4, 2]]

        self.assertEqual(
            m.select_best_estimates(c(est_win), selected_windows1),
                         [[0, 1, 0],
                          [0.25, 0.5, 0.15],
                          [0, 1, 0]])

        self.assertEqual(
            m.select_best_estimates(c(est_win), selected_windows2),
                         [[0, 1, 0],
                          [0.25, 0.5, 0.25],
                          [0, 0.2, 0]])

        est_win = [[{2: deque(),
                     4: deque()},
                    {2: deque(),
                     4: deque()}],
                   [{2: deque(),
                     4: deque()},
                    {2: deque(),
                     4: deque()}]]

        self.assertEqual(
            m.select_best_estimates(c(est_win), [[2, 4], [4, 2]]),
                         [[0.0, 0.0],
                          [0.0, 0.0]])

        self.assertEqual(
            m.select_best_estimates(c(est_win), [[2, 2], [4, 4]]),
                         [[0.0, 0.0],
                          [0.0, 0.0]])

    def test_init_request_windows(self):
        structure = m.init_request_windows(1, 4)
        self.assertEqual(structure, [deque()])
        self.assertEqual(deque_maxlen(structure[0]), 4)

        structure = m.init_request_windows(2, 4)
        self.assertEqual(structure, [deque(),
                                     deque()])
        self.assertEqual(deque_maxlen(structure[0]), 4)
        self.assertEqual(deque_maxlen(structure[1]), 4)

        structure = m.init_request_windows(3, 4)
        self.assertEqual(structure, [deque(),
                                     deque(),
                                     deque()])
        self.assertEqual(deque_maxlen(structure[0]), 4)
        self.assertEqual(deque_maxlen(structure[1]), 4)
        self.assertEqual(deque_maxlen(structure[2]), 4)

    def test_init_variances(self):
        self.assertEqual(m.init_variances([2, 4], 1), [[{2: 1.0,
                                                         4: 1.0}]])
        self.assertEqual(m.init_variances([2, 4], 2), [[{2: 1.0,
                                                         4: 1.0},
                                                        {2: 1.0,
                                                         4: 1.0}],
                                                       [{2: 1.0,
                                                         4: 1.0},
                                                        {2: 1.0,
                                                         4: 1.0}]])
        self.assertEqual(m.init_variances([2, 4], 3), [[{2: 1.0,
                                                         4: 1.0},
                                                        {2: 1.0,
                                                         4: 1.0},
                                                        {2: 1.0,
                                                         4: 1.0}],
                                                       [{2: 1.0,
                                                         4: 1.0},
                                                        {2: 1.0,
                                                         4: 1.0},
                                                        {2: 1.0,
                                                         4: 1.0}],
                                                       [{2: 1.0,
                                                         4: 1.0},
                                                        {2: 1.0,
                                                         4: 1.0},
                                                        {2: 1.0,
                                                         4: 1.0}]])

    def test_init_3_level_structure(self):
        structure = m.init_deque_structure([2, 4], 1)
        self.assertEqual(structure, [[{2: deque(),
                                       4: deque()}]])
        self.assertEqual(deque_maxlen(structure[0][0][2]), 2)
        self.assertEqual(deque_maxlen(structure[0][0][4]), 4)

        structure = m.init_deque_structure([2, 4], 2)
        self.assertEqual(structure, [[{2: deque(),
                                       4: deque()},
                                      {2: deque(),
                                       4: deque()}],
                                     [{2: deque(),
                                       4: deque()},
                                      {2: deque(),
                                       4: deque()}]])
        self.assertEqual(deque_maxlen(structure[0][0][2]), 2)
        self.assertEqual(deque_maxlen(structure[0][0][4]), 4)
        self.assertEqual(deque_maxlen(structure[0][1][2]), 2)
        self.assertEqual(deque_maxlen(structure[0][1][4]), 4)
        self.assertEqual(deque_maxlen(structure[1][0][2]), 2)
        self.assertEqual(deque_maxlen(structure[1][0][4]), 4)
        self.assertEqual(deque_maxlen(structure[1][1][2]), 2)
        self.assertEqual(deque_maxlen(structure[1][1][4]), 4)

        structure = m.init_deque_structure([2, 4], 3)
        self.assertEqual(structure, [[{2: deque(),
                                       4: deque()},
                                      {2: deque(),
                                       4: deque()},
                                      {2: deque(),
                                       4: deque()}],
                                     [{2: deque(),
                                       4: deque()},
                                      {2: deque(),
                                       4: deque()},
                                      {2: deque(),
                                       4: deque()}],
                                     [{2: deque(),
                                       4: deque()},
                                      {2: deque(),
                                       4: deque()},
                                      {2: deque(),
                                       4: deque()}]])
        self.assertEqual(deque_maxlen(structure[0][0][2]), 2)
        self.assertEqual(deque_maxlen(structure[0][0][4]), 4)
        self.assertEqual(deque_maxlen(structure[0][1][2]), 2)
        self.assertEqual(deque_maxlen(structure[0][1][4]), 4)
        self.assertEqual(deque_maxlen(structure[0][2][2]), 2)
        self.assertEqual(deque_maxlen(structure[0][2][4]), 4)
        self.assertEqual(deque_maxlen(structure[1][0][2]), 2)
        self.assertEqual(deque_maxlen(structure[1][0][4]), 4)
        self.assertEqual(deque_maxlen(structure[1][1][2]), 2)
        self.assertEqual(deque_maxlen(structure[1][1][4]), 4)
        self.assertEqual(deque_maxlen(structure[1][2][2]), 2)
        self.assertEqual(deque_maxlen(structure[1][2][4]), 4)
        self.assertEqual(deque_maxlen(structure[2][0][2]), 2)
        self.assertEqual(deque_maxlen(structure[2][0][4]), 4)
        self.assertEqual(deque_maxlen(structure[2][1][2]), 2)
        self.assertEqual(deque_maxlen(structure[2][1][4]), 4)
        self.assertEqual(deque_maxlen(structure[2][2][2]), 2)
        self.assertEqual(deque_maxlen(structure[2][2][4]), 4)

    def test_init_selected_window_sizes(self):
        self.assertEqual(
            m.init_selected_window_sizes([2, 4], 1), [[2]])
        self.assertEqual(
            m.init_selected_window_sizes([2, 4], 2), [[2, 2],
                                                      [2, 2]])
        self.assertEqual(
            m.init_selected_window_sizes([2, 4], 3), [[2, 2, 2],
                                                      [2, 2, 2],
                                                      [2, 2, 2]])


def deque_maxlen(coll):
    return int(re.sub("\)$", "", re.sub(".*=", "", coll.__repr__())))
