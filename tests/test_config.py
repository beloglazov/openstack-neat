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

from neat.config import *


class Config(TestCase):

    @qc
    def read_default_config():
        config = read_config([DEFAILT_CONFIG_PATH])
        assert validate_config(config, REQUIRED_FIELDS)

    @qc
    def read_config():
        config = read_config([DEFAILT_CONFIG_PATH, CONFIG_PATH])
        assert validate_config(config, REQUIRED_FIELDS)

    @qc
    def validate_valid_config(
        x=list_(of=str_(of='abc123_', max_length=20), min_length=0, max_length=10)
    ):
        test_config = dict(zip(x, x))
        assert validate_config(test_config, x)

    @qc
    def validate_invalid_config(
        x=list_(of=str_(of='abc123_', max_length=20), min_length=0, max_length=10),
        y=list_(of=str_(of='abc123_', max_length=20), min_length=0, max_length=10)
    ):
        test_config = dict(zip(x, x))
        if not y:
            assert validate_config(test_config, y)
        else:
            assert not validate_config(test_config, y)
