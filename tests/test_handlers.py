import contextlib
import io
from logging import basicConfig, LogRecord, ERROR, root, WARNING
from random import randint
import unittest

from pytracelog.logging_modules.handlers import StderrHandler, StdoutHandler

SOME_RANDOM_NUMBER = randint(0, 100)


class TestHandlers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Создаем хендлеры и моковые рекорды."""
        cls.err_handler = StderrHandler()
        cls.out_handler = StdoutHandler()
        cls.err_record = LogRecord('error_record', ERROR, 'placeholder_path', SOME_RANDOM_NUMBER, 'ERROR', None, None)
        cls.wrn_record = LogRecord('warn_record', WARNING, 'placeholder_path', SOME_RANDOM_NUMBER, 'WARNING', None, None)

    def test_err_filter_added(self):
        """Проверка добавления фильтров."""
        self.assertEqual(len(self.err_handler.filters), 1)

    def test_wrn_filter_added(self):
        """Проверка добавления фильтров."""
        self.assertEqual(len(self.out_handler.filters), 1)

    def test_err_filter_records(self):
        """Фильтр корректно отрабатывает на сообщения разных уровней."""
        self.assertTrue(StderrHandler.error_record_filter(self.err_record))
        self.assertFalse(StderrHandler.error_record_filter(self.wrn_record))

    def test_wrn_filter_record(self):
        """Фильтр корректно отрабатывает на сообщения разных уровней."""
        self.assertTrue(StdoutHandler.error_record_filter(self.wrn_record))
        self.assertFalse(StdoutHandler.error_record_filter(self.err_record))
