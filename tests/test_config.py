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

import neat.config as config

import logging
logging.disable(logging.CRITICAL)


class Config(TestCase):

    @qc
    def read_default_config():
        paths = [config.DEFAILT_CONFIG_PATH]
        test_config = config.read_config(paths)
        assert config.validate_config(test_config, config.REQUIRED_FIELDS)

    @qc
    def read_config():
        paths = [config.DEFAILT_CONFIG_PATH, config.CONFIG_PATH]
        test_config = config.read_config(paths)
        assert config.validate_config(test_config, config.REQUIRED_FIELDS)

    @qc
    def validate_valid_config(
        x=list_(of=str_(of='abc123_', max_length=20),
                min_length=0, max_length=10)
    ):
        test_config = dict(zip(x, x))
        assert config.validate_config(test_config, x)

    @qc
    def validate_invalid_config(
        x=list_(of=str_(of='abc123_', max_length=20),
                min_length=0, max_length=5),
        y=list_(of=str_(of='abc123_', max_length=20),
                min_length=6, max_length=10)
    ):
        test_config = dict(zip(x, x))
        assert not config.validate_config(test_config, y)

    @qc(10)
    def read_and_validate_valid_config(
        x=list_(of=str_(of='abc123_', max_length=20),
                min_length=0, max_length=10)
    ):
        with MockTransaction:
            test_config = dict(zip(x, x))
            paths = ['path1', 'path2']
            expect(config).read_config(paths).and_return(test_config).once()
            expect(config).validate_config(test_config, x). \
                and_return(True).once()
            assert config.read_and_validate_config(paths, x) == test_config

    @qc(10)
    def read_and_validate_invalid_config(
        x=list_(of=str_(of='abc123_', max_length=20),
                min_length=0, max_length=5),
        y=list_(of=str_(of='abc123_', max_length=20),
                min_length=6, max_length=10)
    ):
        with MockTransaction:
            test_config = dict(zip(x, x))
            paths = [config.DEFAILT_CONFIG_PATH, config.CONFIG_PATH]
            expect(config).read_config(paths).and_return(test_config).once()
            expect(config).validate_config(test_config, y). \
                and_return(False).once()
            try:
                config.read_and_validate_config(paths, y)
            except KeyError:
                assert True
            else:
                assert False
