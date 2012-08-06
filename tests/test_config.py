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

from pyqcy import *

from neat.config import readConfig


class Config(TestCase):

    @qc
    def addition_actually_works(
        x=int_(min=0), y=int_(min=0)
    ):
        the_sum = x + y
        assert the_sum >= x and the_sum >= y
