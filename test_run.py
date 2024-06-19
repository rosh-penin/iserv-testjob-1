from logging import root
from time import sleep

from pytracelog.base import PyTraceLog


if __name__ == '__main__':
    """Создаем логгер, который пишет в logstash немного данных."""
    PyTraceLog.init_logstash_logger()
    while True:
        root.warning("Моковый вывод в stdout")
        root.error("Моковая ошибка для логстеша")
        sleep(60)
