"""
:mod:`handlers` -- Обработчики сообщений
=================================================
.. moduleauthor:: Aleksey Guzhin <a-guzhin@it-serv.ru>
"""
from logging import (
    Handler,
    StreamHandler,
    LogRecord,
    ERROR,
)
from sys import (
    stdout,
    stderr
)

from opentelemetry.trace import (
    get_current_span,
    INVALID_SPAN,
    Status,
    StatusCode,
)


__all__ = (
    'StdoutHandler',
    'StderrHandler',
    'TracerHandler'
)


class StdoutHandler(StreamHandler):
    """
    Вывод записей журнала с уровнем < ERROR в stdout
    """
    def __init__(self, stream=None):
        """
        Переопределение конструктора: потока вывода по-умолчанию - stdout, установка фильтра записей
        """
        super().__init__(stream=stdout if stream is None else stream)
        self.addFilter(self.error_record_filter)

    @staticmethod
    def error_record_filter(record: LogRecord) -> bool:
        """
        Фильтр записей с уровнем лога >= ERROR
        """
        if record.levelno >= ERROR:
            return False
        return True


class StderrHandler(StreamHandler):
    """
    Вывод записей журнала с уровнем >= ERROR в stderr
    """
    def __init__(self, stream=None):
        """
        Переопределение конструктора: установка фильтра записей
        """
        super().__init__(stream=stderr if stream is None else stream)
        self.addFilter(self.error_record_filter)

    @staticmethod
    def error_record_filter(record: LogRecord) -> bool:
        """
        Фильтр записей с уровнем лога < ERROR
        """
        if record.levelno < ERROR:
            return False
        return True


class TracerHandler(Handler):
    """
    Отправка записей журнала в систему трассировки
    """
    def emit(self, record: LogRecord) -> None:
        """
        Создание события для текущего SPAN на основании записи журнала:
         * Наименование - сообщение журнала;
         * Дата создания - дата создания записи журнала;
         * Все все остальные атрибуты () - атрибуте события.

        Кроме этого анализируется текущий уровень записи, и в случае, если он равен или выше уровня ERROR, то для
        SPAN устанавливается статус ERROR

        :param record: Запись лога
        """
        span = get_current_span()
        if span != INVALID_SPAN:
            if record.levelno >= ERROR:
                span.set_status(
                    status=Status(
                        status_code=StatusCode.ERROR
                    )
                )

                # Добавляем в SPAN исключение, если оно есть
                if record.exc_info is not None:
                    span.record_exception(
                        attributes=self.get_record_attrs(record=record, remove_msg=False),
                        exception=record.exc_info[1]
                    )
                    return

            span.add_event(
                name=record.msg,
                attributes=self.get_record_attrs(record=record)
            )

    @staticmethod
    def get_record_attrs(
            record: LogRecord,
            remove_msg: bool = True,
            message_attr_name: str = 'original.message'
    ) -> dict:
        """
        Формирование справочника атрибутов записи.
        При формировании справочника атрибуты 'name', 'msg' (если не задан флаг `remove_msg`), `exc_info`, `exc_text`,
        'msecs', 'relativeCreated' записи игнорируются. Если флаг `remove_msg` не задан, то атрибут 'msg'
        переименовывается в соответствии со значением параметра `message_attr_name`.
        Кроме этого игнорируем атрибуты самого трассировщика: 'otelSpanID', 'otelTraceID' и 'otelServiceName'.

        :param record: Запись лога
        :param remove_msg: Запись лога
        :param message_attr_name: Новое наименование атрибута `msg`

        :return: Справочник атрибутов
        """
        attrs = record.__dict__.copy()

        # Удаляем пустые атрибуты (чтобы в лог не сыпало предупреждениями)
        for k, v in record.__dict__.items():
            if not v:
                attrs.pop(k)

        attrs.pop('name', None)
        attrs.pop('exc_info', None)
        attrs.pop('exc_text', None)
        attrs.pop('msecs', None)
        attrs.pop('relativeCreated', None)
        attrs.pop('otelSpanID', None)
        attrs.pop('otelTraceID', None)
        attrs.pop('otelServiceName', None)

        if remove_msg:
            attrs.pop('msg', None)
        else:
            msg = attrs.pop('msg', None)
            if msg:
                attrs[message_attr_name] = msg

        return attrs
