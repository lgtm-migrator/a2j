"""
https://github.com/Deasilsoft/a2j

Copyright (c) 2020-2022 Deasilsoft

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time
import unittest

from flask import Flask

from ..src.routes import routes


class TestErrors(unittest.TestCase):
    """
    Test errors handling.
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup the testing environment.
        """

        # SETUP FLASK TEST ENVIRONMENT
        app = Flask(__name__)
        routes(app, time.time())
        cls.client = app.test_client()

    def test_record_does_not_exist(self):
        path = "/record/does-not-exist/not-tested/"

        self._test_error(path, 0, "Record does not exist: does-not-exist", self.client.get, 0, 2)
        self._test_error(path, 1, "Invalid commands: ['not-tested']", self.client.get, 1, 2)

    def test_record_direct_path_injection(self):
        path = "/record/../injection.py/version/"

        self._test_error(path, 0, "Record does not exist: ..", self.client.get, 0, 2)
        self._test_error(path, 1, "Invalid commands: ['injection.py']", self.client.get, 1, 2)

    def test_record_traversal_encoding_path_injection(self):
        path = "/record/%2e%2e%2finjection.py/version/"

        self._test_error(path, 0, "Record does not exist: ..", self.client.get, 0, 2)
        self._test_error(path, 1, "Invalid commands: ['injection.py']", self.client.get, 1, 2)

    def test_record_deletion_failure(self):
        path = "/record/does-not-exist/"
        errno = 0
        message = "Record does not exist: does-not-exist"

        self._test_error(path, errno, message, self.client.delete)

    def test_command_does_not_exist(self):
        path = "/record/test.mgz/not-real/fake-command/123/version/"
        errno = 1
        message = "Invalid commands: ['123', 'fake-command', 'not-real']"

        self._test_error(path, errno, message, self.client.get)

    def test_commands_are_empty(self):
        path = "/record/test.mgz/"
        errno = 3
        message = "No commands received."

        self._test_error(path, errno, message, self.client.get)

    def test_minimap_does_not_exist(self):
        path = "/minimap/does-not-exist/not-tested/"
        errno = 0
        message = "Record does not exist: does-not-exist"

        self._test_error(path, errno, message, self.client.get)

    def test_invalid_method(self):
        path = "/record/test.mgz/players/?method=invalid"
        errno = 4
        message = "Invalid method: invalid"

        self._test_error(path, errno, message, self.client.get)

    def test_corrupt_record_summary(self):
        path = "/record/corrupt.aoe2record/players/"
        errno = 2
        message = "Parsing record error: invalid mgz file: could not read enough bytes, expected 1920102207, found 8"

        self._test_error(path, errno, message, self.client.get)

    def test_corrupt_record_match(self):
        path = "/record/corrupt.aoe2record/players/?method=match"
        errno = 2
        message = "Parsing record error: could not parse: Error -3 while decompressing data: invalid block type"

        self._test_error(path, errno, message, self.client.get)

    @staticmethod
    def _test_error(path: str, errno: int, message: str, function: callable, index: int = 0, length: int = 1):
        data = function(path).get_json()

        assert len(data["errors"]) == length
        assert data["errors"][index]["errno"] == errno
        assert data["errors"][index]["message"] == message
