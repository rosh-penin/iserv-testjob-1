from logging import root, WARNING
import unittest

from pytracelog.base import PyTraceLog

NUM_OF_ROOT_HANDLERS = 2
GOOD_LEVELS = (None, 0, 10, 20, 30, 40, 50, "NOTSET", "dEbUg", "info", "WARNING", "ERROR", "CRITICAL")
BAD_LEVELS = ('CRYTICAL', 'bug')


class TestPyTraceLog(unittest.TestCase):

    def test_good_args_for_initroot(self):
        """Проверяем что все ок при 'хороших' аргументах."""
        for level in GOOD_LEVELS:
            with self.subTest():
                PyTraceLog.init_root_logger(level)
                self.assertEqual(len(root.handlers), NUM_OF_ROOT_HANDLERS)
            PyTraceLog.reset()

    def test_bad_args_for_initroot(self):
        """Проверяем что логгинг падает если передать что-то плохое как аргумент."""
        for level in BAD_LEVELS:
            with self.subTest():
                self.assertRaises(ValueError, PyTraceLog.init_root_logger, level)
            PyTraceLog.reset()

    def test_reset_is_working(self):
        """После вызова PyTraceLog.reset должны сброситься фабрики и хендлеры."""
        PyTraceLog.init_root_logger()
        PyTraceLog.reset()
        self.assertEqual(len(root.handlers), 0)
        self.assertEqual(len(PyTraceLog._handlers), 0)
        self.assertIsNone(PyTraceLog._old_factory)
        self.assertEqual(root.level, WARNING)
