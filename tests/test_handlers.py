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

    def test_logger_write_to_pipes(self):
        """
        Извращенный способ тестирование того что данные попадают в нужный поток.
        Контекстные менеджеры тут используются просто чтобы было, но они не работают(Windows).
        По логике вещей они должны перехватывать потоки stdout и stderr, но logging подобное игнорирует.
        Так как PyTraceLog.init_root_logger() жестко задает хендлеры - его тут не использую.
        Именно по этой причине этот тест в test_handlers, хотя по факту должен быть в test_base.
        Можно просто напрямую использовать буферы io.StringIO с менеджером subTest.
        Почему-то StreamHandler (от которого унаследованы все кастомные хандлеры) отрабатывает только с пустым стримом.
        Хоть под капотом в конструкторе он и использует sys.stderr, но если указать его (stream=sys.stderr) вручную - тест валится.
        Не уверен что от этого теста вообще есть польза...
        """
        buffer_stdout = io.StringIO()
        buffer_stderr = io.StringIO()
        with contextlib.redirect_stdout(buffer_stdout), contextlib.redirect_stderr(buffer_stderr):
            basicConfig(handlers=[StderrHandler(buffer_stderr), StdoutHandler(buffer_stdout)])
            root.warning("Этот лог ушел в stdout")
            root.error("А этот - в stderr")
        self.assertIn("stderr", buffer_stderr.getvalue())
        self.assertIn("stdout", buffer_stdout.getvalue())
        for handlr in root.handlers:
            root.removeHandler(handlr)
