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

import neat.locals.overload.mhod.multisize_estimation as estimation
import neat.locals.overload.mhod.core as c

import logging
logging.disable(logging.CRITICAL)


class Core(TestCase):

    def test_init_state(self):
        state = c.init_state(100, [20, 40], 2)
        self.assertEquals(state['previous_state'], 0)
        self.assertEquals(state['previous_utilization'], [])
        self.assertEquals(state['time_in_states'], 0)
        self.assertEquals(state['time_in_state_n'], 0)
        self.assertTrue('request_windows' in state)
        self.assertTrue('estimate_windows' in state)
        self.assertTrue('variances' in state)
        self.assertTrue('acceptable_variances' in state)

    def test_utilization_to_state(self):
        state_config = [0.4, 0.7]
        self.assertEqual(c.utilization_to_state(state_config, 0.0), 0)
        self.assertEqual(c.utilization_to_state(state_config, 0.1), 0)
        self.assertEqual(c.utilization_to_state(state_config, 0.2), 0)
        self.assertEqual(c.utilization_to_state(state_config, 0.3), 0)
        self.assertEqual(c.utilization_to_state(state_config, 0.4), 1)
        self.assertEqual(c.utilization_to_state(state_config, 0.5), 1)
        self.assertEqual(c.utilization_to_state(state_config, 0.6), 1)
        self.assertEqual(c.utilization_to_state(state_config, 0.7), 2)
        self.assertEqual(c.utilization_to_state(state_config, 0.8), 2)
        self.assertEqual(c.utilization_to_state(state_config, 0.9), 2)
        self.assertEqual(c.utilization_to_state(state_config, 1.0), 2)
        self.assertEqual(c.utilization_to_state(state_config, 1.1), 2)

        self.assertEqual(c.utilization_to_state([1.0], 0.0), 0)
        self.assertEqual(c.utilization_to_state([1.0], 0.1), 0)
        self.assertEqual(c.utilization_to_state([1.0], 0.2), 0)
        self.assertEqual(c.utilization_to_state([1.0], 0.3), 0)
        self.assertEqual(c.utilization_to_state([1.0], 0.4), 0)
        self.assertEqual(c.utilization_to_state([1.0], 0.5), 0)
        self.assertEqual(c.utilization_to_state([1.0], 0.6), 0)
        self.assertEqual(c.utilization_to_state([1.0], 0.7), 0)
        self.assertEqual(c.utilization_to_state([1.0], 0.8), 0)
        self.assertEqual(c.utilization_to_state([1.0], 0.9), 0)
        self.assertEqual(c.utilization_to_state([1.0], 1.0), 1)
        self.assertEqual(c.utilization_to_state([1.0], 1.1), 1)

    def test_build_state_vector(self):
        state_config = [0.4, 0.7]
        self.assertEqual(c.build_state_vector(state_config, [0.0, 0.1]),
                         [1, 0, 0])
        self.assertEqual(c.build_state_vector(state_config, [0.0, 0.2]),
                         [1, 0, 0])
        self.assertEqual(c.build_state_vector(state_config, [0.0, 0.3]),
                         [1, 0, 0])
        self.assertEqual(c.build_state_vector(state_config, [0.0, 0.4]),
                         [0, 1, 0])
        self.assertEqual(c.build_state_vector(state_config, [0.0, 0.5]),
                         [0, 1, 0])
        self.assertEqual(c.build_state_vector(state_config, [0.0, 0.6]),
                         [0, 1, 0])
        self.assertEqual(c.build_state_vector(state_config, [0.0, 0.7]),
                         [0, 0, 1])
        self.assertEqual(c.build_state_vector(state_config, [0.0, 0.8]),
                         [0, 0, 1])
        self.assertEqual(c.build_state_vector(state_config, [0.0, 0.9]),
                         [0, 0, 1])
        self.assertEqual(c.build_state_vector(state_config, [0.0, 1.0]),
                         [0, 0, 1])

    def test_get_current_state(self):
        self.assertEqual(c.get_current_state([1, 0, 0]), 0)
        self.assertEqual(c.get_current_state([0, 1, 0]), 1)
        self.assertEqual(c.get_current_state([0, 0, 1]), 2)

    def test_utilization_to_states(self):
        state_config = [0.4, 0.7]
        data = [0.25, 0.30, 0.62, 0.59, 0.67, 0.73, 0.85, 0.97, 0.73,
                0.68, 0.69, 0.52, 0.51, 0.25, 0.38, 0.46, 0.52, 0.55,
                0.58, 0.65, 0.70]
        states = [0, 0, 1, 1, 1, 2, 2, 2, 2, 1, 1,
                  1, 1, 0, 0, 1, 1, 1, 1, 1, 2]
        self.assertEqual(c.utilization_to_states(state_config, data), states)

        state_config = [1.0]
        data = [0.5, 0.5, 1.0, 1.0, 0.5]
        states = [0, 0, 1, 1, 0]
        self.assertEqual(c.utilization_to_states(state_config, data), states)

    def test_issue_command_deterministic(self):
        self.assertEqual(c.issue_command_deterministic([1]), False)
        self.assertEqual(c.issue_command_deterministic([]), True)

    def test_mhod(self):
        state_config = [1.0]
        otf = 0.1
        window_sizes = [30, 40]
        bruteforce_step = 0.5
        learning_steps = 0
        time_step = 300
        migration_time = 20.
        utilization = [1.0]
        state = c.init_state(10, window_sizes, 2)

        with MockTransaction:
            state['previous_utilization'] = []
            expect(estimation).select_best_estimates.and_return([[0., 0.], [0., 0.]])
            expect(c).get_current_state.and_return(1).once()
            decision, _ = c.mhod(state_config, otf, window_sizes, bruteforce_step,
                                 learning_steps, time_step, migration_time, utilization, state)
            self.assertFalse(decision)

        with MockTransaction:
            state['previous_utilization'] = []
            expect(estimation).select_best_estimates.and_return([[0., 0.], [0., 0.]])
            expect(c).get_current_state.and_return(0).once()
            decision, _ = c.mhod(state_config, otf, window_sizes, bruteforce_step,
                                 learning_steps, time_step, migration_time, utilization, state)
            self.assertFalse(decision)

        with MockTransaction:
            state['previous_utilization'] = []
            expect(estimation).select_best_estimates.and_return([[0., 1.], [0., 1.]])
            expect(c).get_current_state.and_return(0).once()
            decision, _ = c.mhod(state_config, otf, window_sizes, bruteforce_step,
                                 learning_steps, time_step, migration_time, utilization, state)
            self.assertFalse(decision)

        with MockTransaction:
            state['previous_utilization'] = []
            expect(estimation).select_best_estimates.and_return([[0., 1.], [0., 1.]])
            expect(c).get_current_state.and_return(1).once()
            decision, _ = c.mhod(state_config, otf, window_sizes, bruteforce_step,
                                 learning_steps, time_step, migration_time, utilization, state)
            self.assertTrue(decision)

#        with MockTransaction:
#            utilization = [1.0, 1.0]
#            state['previous_utilization'] = [1.0, 1.0]
#            state['time_in_states'] = 2
#            expect(estimation).select_best_estimates.never()
#            decision, _ = c.mhod(state_config, otf, window_sizes, bruteforce_step,
#                                 learning_steps, time_step, migration_time, utilization, state)
#            self.assertFalse(decision)


def deque_maxlen(coll):
    return int(re.sub("\)$", "", re.sub(".*=", "", coll.__repr__())))
